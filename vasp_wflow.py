import os
import json
from fireworks import LaunchPad
from atomate2.vasp.flows.core import DoubleRelaxMaker
from jobflow.managers.fireworks import flow_to_workflow
from pymatgen.core import Structure

# submit each workflow to the FireWorks launchpad
lpad = LaunchPad.auto_load()

# load all of the structure objects in 'templates' into a list
structure_path = "/home/knykiel/projects/MXene_stacking/relaxed_templates"
for filename in os.listdir(structure_path):
    if filename.endswith(".vasp"):
        struct = Structure.from_file(os.path.join(structure_path, filename))

        # perform a double relaxation on the structure
        relax_flow = DoubleRelaxMaker(name=filename).make(struct)
        wf = flow_to_workflow(relax_flow)
        lpad.add_wf(wf)
