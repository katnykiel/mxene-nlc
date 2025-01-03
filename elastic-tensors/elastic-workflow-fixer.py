from fireworks import LaunchPad, Firework
from collections import Counter
from kat.atomate2.utils import continue_firework
from atomate2.vasp.flows.elastic import ElasticMaker
from atomate2.vasp.powerups import update_user_incar_settings
from jobflow.managers.fireworks import flow_to_workflow

# create a LaunchPad object
launchpad = LaunchPad.auto_load()

# query for all workflows that are dft-elastic
pattern = ".*DFT elastic.*"
workflows = launchpad.workflows.find({"name": {"$regex": pattern}})

ids = []

for workflow in workflows:
    
    # remove workflows where the status of all fireworks is completed
    if Counter(workflow["fw_states"].values())["COMPLETED"] == len(workflow["fw_states"]):
        continue

    # filter for workflows with completed generate_elastic_deformations by looking for a length of more 10 in parent_links
    if len(workflow["fw_states"]) < 10:

        continue

        # get the highest ID
        max_id = max([int(id) for id in workflow["fw_states"].keys()])

        # check that this is tight relax 1
        tight_relax_1_fw = launchpad.get_fw_by_id(max_id)
        if tight_relax_1_fw.name != "tight relax 1":
            print(f"Workflow {workflow['name']} does not have tight_relax_1 as the last firework, try another method?")
            continue
        
        # Get the structure of this firework
        struct = tight_relax_1_fw.spec['_tasks'][0]['job'].function_args[0]

        # Get the ID of this workflow
        workflow_id = launchpad.get_wf_ids(workflow)[0]

        # Delete the workflow
        launchpad.delete_wf(workflow_id)
        
        # Create a new elastic workflow with this structure
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
        launchpad.add_wf(wf)

    # get IDs of named fireworks, stored as strings
    max_key = None
    max_value = []
    for key, value in workflow["parent_links"].items():
        if len(value) > len(max_value):
            max_key = key
            max_value = value

    store_inputs_id = max_key
    elastic_relax_ids = [str(id) for id in workflow["parent_links"][store_inputs_id]]
    fit_elastic_tensor_id = None

    for key, value in workflow["parent_links"].items():
        if int(store_inputs_id) in value:
            fit_elastic_tensor_id = key
            break

    # for each ID in elastic_relax_ids, make an if s tatement for those that fizzle
    for id in elastic_relax_ids:
        if workflow["fw_states"][id] == "FIZZLED":
            try:
                continue_firework(int(id))
                print(f"Continued firework {id}")
            except:
                print(f"Could not continue firework {id}")

print(ids)