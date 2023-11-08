# query the relaxed DFT structures and energies from the atomate2 mongodb
from jobflow import SETTINGS
import json
from pymatgen.core import Structure

store = SETTINGS.JOB_STORE

# connect to the job store (mongodb)
store.connect()

# results = store.query({"output.formula_pretty": "Ta4C3"})
for tag in ["M4X3", "M3X2", "M2X"]:
    results = store.query(
        {"metadata.tags": {"$in": [f"{tag}-templates"]}, "name": "relax 2"}
    )

    # print the results for debugging
    saved_results = {"structures": [], "energies": []}

    for i, result in enumerate(results):
        print(result)
        saved_results["structures"].append(result["output"]["structure"])
        saved_results["energies"].append(result["output"]["output"]["energy"])

        # write each of the individual structures to a file
        # (for debugging)
        struct = Structure.from_dict(result["output"]["structure"])
        struct.to(filename=f"{tag}/relaxed_structs/structure_{i}.vasp", fmt="poscar")

    # write to file
    with open(f"{tag}/relaxed_structs.json", "w") as f:
        json.dump(saved_results, f)
