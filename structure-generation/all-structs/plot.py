from pymatgen.core import Structure

# Specify the path to your crystal structure file
structure_file = "/home/knykiel/projects/mxene-nlc/structure-generation/all-structs/BACB-CBAC.vasp"

# Load the crystal structure from the file
structure = Structure.from_file(structure_file)

from pymatgen.io.ase import AseAtomsAdaptor
from ase.visualize import view

# Convert pymatgen Structure to ase Atoms
adaptor = AseAtomsAdaptor()
ase_atoms = adaptor.get_atoms(structure)

# Visualize the structure
view(ase_atoms)