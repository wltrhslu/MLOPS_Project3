import great_expectations as gx
import os

BASE_PATH = "/workspaces/MLOPS_Project3/"

context = gx.get_context(
    mode="file", project_root_dir=os.path.join(BASE_PATH, "./")
)
checkpoint_name = "my_checkpoint"
checkpoint = context.checkpoints.get(checkpoint_name)

result = checkpoint.run()

# View the Data Docs
context.open_data_docs()
