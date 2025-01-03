import os
from fireworks import LaunchPad
from atomate2.vasp.flows.core import DoubleRelaxMaker
from jobflow.managers.fireworks import flow_to_workflow
from pymatgen.core import Structure
from matglrelaxer.relaxer import relax_structure

from atomate2.vasp.powerups import (
    update_user_incar_settings,
    update_user_kpoints_settings,
)
from jobflow.managers.fireworks import flow_to_workflow
from pymatgen.io.vasp.inputs import Kpoints

# submit each workflow to the FireWorks launchpad
lpad = LaunchPad.auto_load()

KPOINTS = [6, 9, 12, 15, 18]
KSPACINGS = [2 * 3.14 / (k * 3) for k in KPOINTS]

# convergence parameters testing
for KSPACING in KSPACINGS:
    for ENCUT in [400, 450, 500, 550, 600]:
        # get Ta4C3 template structure
        structure_path = (
            f"/home/knykiel/projects/mxene-nlc/M4X3/relaxed_structs/BACB-CBAC-ACBA.vasp"
        )
        struct = Structure.from_file(structure_path)

        # remap to Ti4N3, for a different template
        struct.replace_species({"Ta": "Ti", "C": "N"})

        # relax the structure with matgl
        relax_struct = relax_structure(struct)

        # perform a double relaxation on the structure
        relax_flow = DoubleRelaxMaker(
            name=f"convergence testing: k={KSPACING}, E={ENCUT}"
        ).make(relax_struct)

        # Update the INCAR parameters
        incar_updates = {"ENCUT": ENCUT, "NCORE": 8, "KSPACING": KSPACING}

        relax_flow = update_user_incar_settings(relax_flow, incar_updates)

        # add the workflow to the launchpad
        wf = flow_to_workflow(relax_flow)
        for fw in wf.fws:
            fw.spec.update({"tags": ["convergence-testing"]})

        lpad.add_wf(wf)
