# get a list of all the unique space groups for our systems 
from fireworks import LaunchPad
from jobflow import SETTINGS
from atomate2.vasp.powerups import update_user_incar_settings
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
from fireworks import LaunchPad
from jobflow.managers.fireworks import flow_to_workflow
from pymatgen.core import Structure

# connect to the job store (mongodb)
store = SETTINGS.JOB_STORE
store.connect()
lpad = LaunchPad.auto_load()
results = store.query({"metadata.tags": {"$all": ["mxene-nlc"]}, "name": "relax 2"})
space_groups = {}
for result in results:
    struct = Structure.from_dict(result["output"]["structure"])
    sg = SpacegroupAnalyzer(struct).get_space_group_number()
    if sg not in space_groups:
        space_groups[sg] = 1
    else:
        space_groups[sg] += 1

for sg, count in space_groups.items():
    print(f"Space Group {sg}: {count} occurrences")