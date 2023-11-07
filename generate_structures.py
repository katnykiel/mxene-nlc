# Import libraries
from pymatgen.core import Structure, Lattice
from pymatgen.core.operations import SymmOp
import itertools
import os


def rotate_structure(structure, angle, axis):
    """Rotate a structure about an axis

    Args:
        structure (Structure): pymatgen Structure object
        angle (float): angle in degrees to rotate the structure
        axis (list): axis to rotate the structure about

    Returns:
        Structure: rotated structure
    """

    struct = structure.copy()

    # Define the rotation operation
    rotation = SymmOp.from_axis_angle_and_translation(axis, angle, False, [0, 0, 0])

    # Rotate the structure by iterating through the sites
    for site in struct:
        site.frac_coords = rotation.operate(site.frac_coords)

    return struct


def translate_structure(structure, translation):
    """Translate a structure by a translation vector

    Args:
        structure (Structure): pymatgen Structure object
        translation (list): translation vector
    Returns:
        Structure: translated structure
    """

    struct = structure.copy()

    # Translate the structure by iterating through the sites
    for site in struct:
        site.frac_coords += translation

    return struct


def stack_structures(*structures):
    """
    Stack a list of structures on top of each other in the order they were passed

    Args:
        *structures (Structure): variable number of pymatgen Structure objects to be stacked

    Returns:
        Structure: stacked structure
    """
    # Create a copy of the first structure
    stacked_structure = structures[0].copy()

    # Get the lattice parameters of the first structure
    a, b, c = stacked_structure.lattice.abc

    # Iterate over the remaining structures and stack them on top of the first structure
    for i, structure in enumerate(structures[1:]):
        # Translate the current structure to the top of the stacked structure
        structure_translated = translate_structure(structure, [0, 0, i + 1])

        # Add the current structure to the stacked structure by sites
        for site in structure_translated.copy():
            stacked_structure.append(site.species_string, site.frac_coords)

    # Adjust the lattice parameters to fix the unit cell
    lattice = stacked_structure.lattice
    al, bl, cl, alpha, beta, gamma = lattice.parameters

    # Create a new Lattice with the modified a and b parameters
    new_lattice = Lattice.from_parameters(
        a=al, b=bl, c=cl * len(structures), alpha=alpha, beta=beta, gamma=gamma
    )

    # Assign the new lattice to the structure
    stacked_structure.lattice = new_lattice

    # Adjust the fractional coordinates to match the new lattice
    for site in stacked_structure:
        site.frac_coords[2] = site.frac_coords[2] / len(structures)

    return stacked_structure.copy()


def generate_structures(structure, n=[2, 3], angles=[0, 180]):
    """
    Generate stacked MXene structures, with translation to three lattice sites and rotation by 60 degrees

    Args:
        structure (Structure): pymatgen Structure object, representing a single MXene flake
        n (list of int): number of layers to stack up to, default is [1, 2, 3]
        angles (list of float): angles in degrees to rotate the structure by, default is [0, 30, 60, 90]

    Returns:
        list of Structure: list of all stacked MXene structures
    """

    # Initialize list of structures
    structures = [structure]

    # Generate all combinations of angles and translations
    angle_trans_combinations = list(
        itertools.product(angles, [[0, 0, 0], [1 / 3, 2 / 3, 0], [2 / 3, 1 / 3, 0]])
    )

    # Loop over number of layers to stack
    for i in n:
        # Generate all combinations of angles and translations for the current number of layers
        layer_combinations = list(
            itertools.product(angle_trans_combinations, repeat=i - 1)
        )

        [print(combination) for combination in layer_combinations]

        # Loop over all combinations of angles and translations
        for combination in layer_combinations:
            # Create a list of structures to stack
            structures_to_stack = [structure]

            # Loop over all angles and translations in the current combination
            for angle, translation in combination:
                # Rotate the structure
                rotated_structure = rotate_structure(structure, angle, [0, 0, 1])

                # Translate the structure
                translated_structure = translate_structure(
                    rotated_structure, translation
                )

                # Add the translated structure to the list of structures to stack

                structures_to_stack.append(translated_structure)

            # Stack the structures
            stacked_structure = stack_structures(*structures_to_stack)

            # Add the stacked structure to the list of structures
            structures.append(stacked_structure)

    print("Total structures: ", len(structures))

    return structures


def remove_redundant_structures(structures):
    """
    Remove redundant structures from a list of pymatgen.core.Structure objects.

    Args:
        structures (list): A list of pymatgen.core.Structure objects.

    Returns:
        list: A list of unique pymatgen.core.Structure objects.
    """

    # Check for exact matches first
    sorta_unique_structures = []
    for s in structures:
        if s not in sorta_unique_structures:
            sorta_unique_structures.append(s)

    # Now look to see if any structure is just another one, offset by a translation of [1/3,2/3,0],[2/3,1/3,0]]
    unique_structures = []
    for i, s in enumerate(sorta_unique_structures):
        is_unique = True
        for trans in [
            [1 / 3, 2 / 3, 0],
            [2 / 3, 1 / 3, 0],
            [1 / 3, 1 / 3, 1 / 3],
            [2 / 3, 2 / 3, 2 / 3],
        ]:
            s_trans = translate_structure(s, trans)
            if any(
                [
                    s_trans.matches(s2, ltol=1e-3, stol=1e-3)
                    for s2 in sorta_unique_structures[i + 1 :]
                ]
            ):
                is_unique = False
                break
        if is_unique:
            unique_structures.append(s)

    print("Unique structures: ", len(unique_structures))

    return unique_structures


def remove_unstable_structures(structures):
    """Remove structures which are have two Ta atoms next to each other when sorting by z and share the same x,y coords"""

    stable_structures = []

    for s in structures:
        # Sort the sites by z-coordinate
        sorted_sites = sorted(s.sites, key=lambda site: site.coords[2])

        # Check if there are two Ta atoms next to each other with the same x,y coords
        found_unstable = False
        for i in range(len(sorted_sites)):
            site1, site2 = sorted_sites[i], sorted_sites[(i + 1) % len(sorted_sites)]
            if (
                site1.species_string == "Ta"
                and site2.species_string == "Ta"
                and all(site1.coords[:2] == site2.coords[:2])
            ):
                found_unstable = True
                break
        if not found_unstable:
            # If no unstable configuration was found, add the structure to the list of stable structures
            stable_structures.append(s)

    print("Stable structures: ", len(stable_structures))
    return stable_structures


def write_structures_to_folder(dir_name, structures, filenames=None):
    """
    Write a list of pymatgen.core.Structure objects to a directory of VASP files.

    Args:
        dir_name (str): The directory to write the VASP files to.
        structures (list): A list of pymatgen.core.Structure objects.
        filenames (list): A list of filenames to use for the VASP files. If None, use default naming convention.

    Returns:
        None
    """
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    for i, s in enumerate(structures):
        if filenames is not None and i < len(filenames):
            filename = os.path.join(dir_name, f"{filenames[i]}.vasp")
        else:
            filename = os.path.join(dir_name, f"structure_{i}.vasp")
        s.to(filename=filename, fmt="poscar")


def get_structures_from_folder(
    dir_name="/home/knykiel/projects/mxene-nlc/stacked_structs",
):
    """
    Load in all structures from a directory of VASP files.

    Args:
        dir_name (str): The directory containing the VASP files.

    Returns:
        list: A list of pymatgen.core.Structure objects.
    """
    structures = []
    for filename in os.listdir(dir_name):
        if filename.endswith(".vasp"):
            filepath = os.path.join(dir_name, filename)
            structure = Structure.from_file(filepath)
            structures.append(structure)
    return structures


def get_ordering_names(dir_name, n=2):
    # Read in structures from dir_name
    structures = get_structures_from_folder(dir_name)

    # Look at all of the Ta atoms and assign them either A, B, or C depending on their x,y coords
    # let B=0,0; A=1/3,2/3; C=2/3,1/3 sorted by z from largest to smallest
    ordering_names = []
    for s in structures:
        # Sort the sites by z-coordinate
        sorted_sites = sorted(s.sites, key=lambda site: site.coords[2])
        # Get the coordinates of the Ta atoms
        ta_coords = [
            site.frac_coords for site in sorted_sites if site.species_string == "Ta"
        ]
        ordering = []
        for coord in ta_coords:
            x, y, z = coord
            if (
                abs(round(3 * x) / 3 - 0) % 1 < 0.01
                and abs(round(3 * y / 3) - 0) % 1 < 0.01
            ):
                ordering.append("B")
            elif abs(x - 1 / 3) % 1 < 0.01 and abs(y - 2 / 3) % 1 < 0.01:
                ordering.append("A")
            elif abs(x - 2 / 3) % 1 < 0.01 and abs(y - 1 / 3) % 1 < 0.01:
                ordering.append("C")

        ordering_names.append("".join(ordering))

    # Add "-" every n letters
    for i in range(len(ordering_names)):
        ordering_names[i] = "-".join(
            [ordering_names[i][j : j + n] for j in range(0, len(ordering_names[i]), n)]
        )

    # Save the structure to a folder "final_structs" with the name "{ordering}.vasp"
    write_structures_to_folder(
        "/home/knykiel/projects/mxene-nlc/M2X/final_structs",
        structures,
        ordering_names,
    )


# load M2X structure
struct = Structure.from_file("/home/knykiel/projects/mxene-nlc/M2X/M2X_monolayer.vasp")
structs = generate_structures(struct)
write_structures_to_folder(
    "/home/knykiel/projects/mxene-nlc/M2X/stacked_structs", structs
)
structs = get_structures_from_folder(
    "/home/knykiel/projects/mxene-nlc/M2X/stacked_structs"
)
unique_structs = remove_redundant_structures(structs)
write_structures_to_folder(
    "/home/knykiel/projects/mxene-nlc/M2X/unique_structs", unique_structs
)
structs = get_structures_from_folder(
    "/home/knykiel/projects/mxene-nlc/M2X/unique_structs"
)
stable_structs = remove_unstable_structures(structs)
write_structures_to_folder(
    "/home/knykiel/projects/mxene-nlc/M2X/stable_structs", stable_structs
)
get_ordering_names("/home/knykiel/projects/mxene-nlc/M2X/stable_structs")
