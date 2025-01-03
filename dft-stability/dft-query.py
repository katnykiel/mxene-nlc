# query the relaxed DFT structures and energies from the atomate2 mongodb
from jobflow import SETTINGS
import json
from pymatgen.core import Structure
from pymatgen.analysis.phase_diagram import PhaseDiagram, PDPlotter
from pymatgen.entries.compatibility import MaterialsProjectCompatibility
from pymatgen.entries.computed_entries import ComputedEntry

store = SETTINGS.JOB_STORE


# connect to the job store (mongodb)
store.connect()

results = store.query(
    {
        "metadata.tags": {"$in": ["mxene-nlc"]},
        "name": "relax 2",
    }
)

results = get_formation_energy(results)

# print the results for debugging
saved_results = {
    "structures": [],
    "energies": [],
    "input_structures": [],
    "formation_energies": [],
}

for i, result in enumerate(results):
    saved_results["structures"].append(result["output"]["structure"])
    saved_results["input_structures"].append(result["output"]["input"]["structure"])
    saved_results["energies"].append(result["output"]["output"]["energy_per_atom"])
    saved_results["formation_energies"].append(result["formation_energy"])

# write to file
with open(f"dft-results.json", "w") as f:
    json.dump(saved_results, f)
