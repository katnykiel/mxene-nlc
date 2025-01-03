# query the relaxed DFT structures and energies from the atomate2 mongodb
from jobflow import SETTINGS
import json
from pymatgen.core import Structure
from pymatgen.analysis.phase_diagram import PhaseDiagram, PDPlotter
from pymatgen.entries.compatibility import MaterialsProjectCompatibility
from pymatgen.entries.computed_entries import ComputedEntry

store = SETTINGS.JOB_STORE

from kat.atomate2 import get_formation_energy

# connect to the job store (mongodb)
store.connect()


def get_ordering_name(structure):
    ordering = []
    # Sort the sites by z-coordinate
    sorted_sites = sorted(structure.sites, key=lambda site: site.coords[2])
    # Get the coordinates of the M atoms (excluding C and N)
    M_coords = [
        site.frac_coords
        for site in sorted_sites
        if site.species_string not in ["C", "N"]
    ]

    tol = 0.1
    for coord in M_coords:
        x, y, z = coord
        while x < -0.17 or x > 0.83:
            if x < -0.17:
                x += 1
            elif x > 0.83:
                x -= 1
        while y < -0.17 or y > 0.83:
            if y < -0.17:
                y += 1
            elif y > 0.83:
                y -= 1

        if abs(x - 1 / 3) <= tol and abs(y - 2 / 3) <= tol:
            ordering.append("A")
        elif abs(x - 0) <= tol and abs(y - 0) <= tol:
            ordering.append("B")
        elif abs(x - 2 / 3) <= tol and abs(y - 1 / 3) <= tol:
            ordering.append("C")

    ordering_name = "".join(ordering)
    return ordering_name


results = store.query(
    {
        "metadata.tags": {
            "$in": [
                "Ta-C",
                "elastic",
            ]
        },
        "name": "fit_elastic_tensor",
    }
)

# write to file
saved_results = []
for result in results:
    derived_properties = result["output"]["derived_properties"]
    structure = Structure.from_dict(result["output"]["input"]["structure"])
    saved_results.append(
        {
            "derived_properties": derived_properties,
            "ordering": get_ordering_name(structure),
        }
    )

    # print the structure and the ordering name
    print(structure)
    print(get_ordering_name(structure))

# Print the ordering names
for result in saved_results:
    print(result["ordering"])
