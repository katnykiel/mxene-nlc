# query the relaxed DFT structures and energies from the atomate2 mongodb
import json
import os

from pymatgen.core import Structure
from jobflow import SETTINGS
from fireworks import LaunchPad
from atomate2.vasp.flows.core import DoubleRelaxMaker
from atomate2.vasp.powerups import update_user_incar_settings
from jobflow.managers.fireworks import flow_to_workflow
from matglrelaxer.relaxer import relax_structure

store = SETTINGS.JOB_STORE

# connect to the job store (mongodb)
store.connect()
lpad = LaunchPad.auto_load()

# results = store.query({"output.formula_pretty": "Ta4C3"})
for tag in ["M4X3", "M3X2", "M2X"]:
    results = store.query(
        {"metadata.tags": {"$in": [f"{tag}-templates"]}, "name": "relax 2"}
    )
    # Get template structures
    structs = [Structure.from_dict(result["output"]["structure"]) for result in results]

    # Ignore the first 2 results for the M4X3 tag, due to the incomplete run
    if tag == "M4X3":
        structs = structs[2:]

    for struct in structs:
        for M in ["Ta", "Ti", "Hf", "Zr", "Nb", "Mo", "V", "W", "Sc", "Cr", "Mn"]:
            for X in ["C", "N"]:
                # replace the species in the template structure
                struct.replace_species({"Ta": M, "C": X})

                # relax the structure with matgl
                relax_struct = relax_structure(struct)

                # perform a double relaxation on the structure
                relax_flow = DoubleRelaxMaker(name=f"{tag}:{M}-{X}").make(relax_struct)

                # Update the INCAR parameters
                incar_updates = {"ENCUT": 550, "NCORE": 8, "GGA": "PE"}

                relax_flow = update_user_incar_settings(relax_flow, incar_updates)

                # add the workflow to the launchpad
                wf = flow_to_workflow(relax_flow)
                for fw in wf.fws:
                    fw.spec.update({"tags": [tag, "nlc", f"{M}{X}"]})
                lpad.add_wf(wf)
