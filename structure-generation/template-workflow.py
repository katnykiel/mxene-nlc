import os
from fireworks import LaunchPad
from atomate2.vasp.flows.core import DoubleRelaxMaker
from jobflow.managers.fireworks import flow_to_workflow
from pymatgen.core import Structure
from matglrelaxer.relaxer import relax_structure

from atomate2.vasp.powerups import update_user_incar_settings
from jobflow.managers.fireworks import flow_to_workflow

# submit each workflow to the FireWorks launchpad
lpad = LaunchPad.auto_load()

templates = ["M4X3", "M3X2", "M2X"]

for template in templates:
    # load all of the structure objects in 'templates' into a list
    structure_path = f"/home/knykiel/projects/mxene-nlc/{template}/final_structs"
    for filename in os.listdir(structure_path):
        struct = Structure.from_file(os.path.join(structure_path, filename))

        # relax the structure with matgl
        relax_struct = relax_structure(struct)

        # perform a double relaxation on the structure
        relax_flow = DoubleRelaxMaker(name=filename).make(relax_struct)

        # Update the INCAR parameters
        incar_updates = {
            "ENCUT": 500,
            "NCORE": 8,
            "GGA": "PE",
        }

        relax_flow = update_user_incar_settings(relax_flow, incar_updates)

        # add the workflow to the launchpad
        wf = flow_to_workflow(relax_flow)
        for fw in wf.fws:
            fw.spec.update({"tags": [f"{template}-templates"]})
        lpad.add_wf(wf)
