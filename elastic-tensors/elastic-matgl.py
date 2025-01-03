from pymatgen.core import Structure
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

from fireworks import LaunchPad
from atomate2.forcefields.flows.elastic import ElasticMaker
from atomate2.forcefields.jobs import M3GNetRelaxMaker
from jobflow.managers.fireworks import flow_to_workflow

from jobflow import SETTINGS

store = SETTINGS.JOB_STORE

# connect to the job store (mongodb)
store.connect()
lpad = LaunchPad.auto_load()

results = store.query({"metadata.tags": {"$all": ["mxene-nlc"]}, "name": "relax 2"})

structures = []

for result in results:
    struct = Structure.from_dict(result["output"]["structure"])
    structures.append(struct)

for s in structures[:1]:
    sga = SpacegroupAnalyzer(s)
    struct = sga.get_primitive_standard_structure()

    elastic_flow = ElasticMaker(
        name=f"GNN elastic test: {struct.formula}",
        bulk_relax_maker=M3GNetRelaxMaker(
            relax_cell=True, relax_kwargs={"fmax": 0.00001}
        ),
        elastic_relax_maker=M3GNetRelaxMaker(
            relax_cell=False, relax_kwargs={"fmax": 0.00001}
        ),
    ).make(struct)
    wf = flow_to_workflow(elastic_flow)
    for fw in wf.fws:
        fw.spec.update(
            {
                "tags": [
                    "elastic-gnn-test",
                ]
            }
        )
    lpad.add_wf(wf)
