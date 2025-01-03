# query materials project for all structures with our space groups and compositions
from mp_api.client import MPRester

space_groups = [186, 166, 164, 156]
M_elements = ["Ta", "Ti", "Hf", "Zr", "Nb", "Mo", "V", "W", "Sc", "Cr", "Mn"]
X_elements = ["C", "N"]

outputs = []
output_data = []

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

with MPRester() as mpr:
    for M in M_elements:
        for X in X_elements:
            for sg in space_groups:
                data = mpr.materials.search(spacegroup_number=sg, elements=[M, X], num_elements=(2,2), formula=[f"A4B3", "A3B2", "A2B"])
                for d in data:
                    if d.formula_pretty in [f"{M}4{X}3", f"{M}3{X}2", f"{M}2{X}"]: # type: ignore
                        outputs.append(f"{d.formula_pretty}: {sg}, {d.material_id}") # type: ignore
                        output_data.append(d)

[print(o) for o in outputs]

for result in results:
    struct = Structure.from_dict(result["output"]["structure"])
    sg = SpacegroupAnalyzer(struct, symprec=.1).get_space_group_number()
    for mp_struct in output_data:
        if sg == mp_struct.symmetry.number and mp_struct.composition.formula == struct.composition.formula:
            print(f"found a match at {mp_struct.material_id}: this is where we should compare lattice vectors")
            break



