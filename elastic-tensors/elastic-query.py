# query the relaxed DFT structures and energies from the atomate2 mongodb
from fireworks import LaunchPad
from kat.atomate2.utils import save_docs_to_df
from jobflow import SETTINGS

store = SETTINGS.JOB_STORE

# connect to the job store (mongodb)
store.connect()
lpad = LaunchPad.auto_load()

# Query for the relaxation simulations
docs = store.query(
    {
        "metadata.tags": {
            "$all": [
                "elastic-dft-workflow",
            ]
        },
        "name": "tight relax 2",
    }
)

save_docs_to_df(docs, "elastic-relax-docs.json")


# Query for the elastic tensor simulations
docs = store.query(
    {
        "metadata.tags": {
            "$all": [
                "elastic-dft-workflow",
            ]
        },
        "name": "fit_elastic_tensor",
    }
)

save_docs_to_df(docs, "elastic-results.json")
