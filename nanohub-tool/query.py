from fireworks import LaunchPad
from jobflow import SETTINGS
import json

# connect to the launchpad (mongodb)
lp = LaunchPad.auto_load()

# query the launchpad for a sample workflow and get the corresponding fireworks
wf = lp.workflows.find_one({"nodes": 93701})

# write the workflow to a json file
with open("workflow.json", "w") as f:
    json.dump(wf['links'], f, default=str)

# connect to the job store (mongodb)
store = SETTINGS.JOB_STORE
store.connect()

# query the job store for the fireworks in the given workflow
fw_docs = list(store.query({"metadata.fw_id": {"$in": wf['nodes']}}))

# write the fireworks to a json file
with open("fireworks.json", "w") as f:
    json.dump(fw_docs, f, default=str)
