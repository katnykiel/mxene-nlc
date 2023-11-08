# query the relaxed DFT structures and energies from the atomate2 mongodb
from jobflow import SETTINGS
import json
from pymatgen.core import Structure

store = SETTINGS.JOB_STORE

# connect to the job store (mongodb)
store.connect()

results = store.query(
    {"metadata.tags": {"$in": [f"convergence-testing"]}, "name": "relax 1"}
)

# print the results for debugging
saved_results = {
    "structures": [],
    "energies": [],
    "ENCUT": [],
    "KPOINTS": [],
    "run_time": [],
}

for i, result in enumerate(results):
    print(result)
    saved_results["structures"].append(result["output"]["structure"])
    saved_results["energies"].append(result["output"]["output"]["energy"])
    saved_results["ENCUT"].append(
        result["output"]["calcs_reversed"][-1]["input"]["incar"]["ENCUT"]
    )
    saved_results["KPOINTS"].append(
        result["output"]["calcs_reversed"][-1]["input"]["kpoints"]["kpoints"][0][0]
    )
    saved_results["run_time"].append(
        result["output"]["run_stats"]["overall"]["user_time"]
    )

# write to file
with open(f"converged_structs.json", "w") as f:
    json.dump(saved_results, f)
