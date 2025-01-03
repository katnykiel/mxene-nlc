# query the relaxed DFT structures and energies from the atomate2 mongodb
import json
import os

from pymatgen.core import Structure, Lattice
from jobflow import SETTINGS
from fireworks import LaunchPad
from atomate2.vasp.flows.core import DoubleRelaxMaker
from atomate2.vasp.powerups import update_user_incar_settings
from jobflow.managers.fireworks import flow_to_workflow
from matglrelaxer.relaxer import relax_structure
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
from atomate2.vasp.flows.elastic import ElasticMaker

store = SETTINGS.JOB_STORE

# connect to the job store (mongodb)
store.connect()
lpad = LaunchPad.auto_load()

results = store.query({"metadata.tags": {"$all": ["mxene-nlc"]}, "name": "relax 2"})

structures = []
for result in results:
    struct = Structure.from_dict(result["output"]["structure"])
    structures.append(struct)

for struct in structures:
    # Symmetrize the structure
    sga = SpacegroupAnalyzer(struct)
    struct = sga.get_primitive_standard_structure()

    # Get the elastic constants
    elastic_flow = ElasticMaker(name=f"DFT elastic: {struct.formula}").make(struct)

    # Update the INCAR parameters
    incar_updates = {"NCORE": 9, "GGA": "PE"}

    elastic_flow = update_user_incar_settings(elastic_flow, incar_updates)

    # add the workflow to the launchpad
    wf = flow_to_workflow(elastic_flow)
    for fw in wf.fws:
        fw.spec.update(
            {
                "tags": [
                    "elastic-dft-workflow",
                ]
            }
        )
    lpad.add_wf(wf)
