from fireworks import LaunchPad
from jobflow import SETTINGS

# Connect to the job store and launchpad
store = SETTINGS.JOB_STORE
store.connect()
lpad = LaunchPad.auto_load()

# change this to be the fw id of the "fit_elastic_tensor" job
fw_id = 19325

fw = lpad.get_fw_by_id(fw_id)
job = fw[0]["job"]
job.resolve_args(store=store)
