# query the relaxed DFT structures and energies from the atomate2 mongodb
from jobflow import SETTINGS
import json
from pymatgen.core import Structure

store = SETTINGS.JOB_STORE

# connect to the job store (mongodb)
store.connect()

results = store.query({"metadata.tags": {"$in": [f"nlc"]}, "name": "relax 2"})

# print the results for debugging
saved_results = {
    "structures": [],
    "energies": [],
}

for i, result in enumerate(results):
    print(result)
    saved_results["structures"].append(result["output"]["structure"])
    saved_results["energies"].append(result["output"]["output"]["energy"])

# write to file
with open(f"dft-results.json", "w") as f:
    json.dump(saved_results, f)
