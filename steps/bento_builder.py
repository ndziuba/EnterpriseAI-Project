# Import the step
from zenml.integrations.bentoml.steps import bento_builder_step
from datetime import datetime

# The name we gave to our deployed model
MODEL_NAME = "wf_model"


# Call the step with the parameters
bento_builder = bento_builder_step.with_options(
    parameters=dict(
        model_name=MODEL_NAME, 
        model_type="tensorflow", 
        service="service.py:svc",  # Path to the service file within zenml repo
        labels={  # Labels to be added to the bento bundle
            "framework": "tensorflow",
            "dataset": "base_dataset_"+ str(datetime.now()),
            "zenml_version": "0.41",
        },
        exclude=[".dvc", "data", "models", "notebooks"],  # Exclude files from the bento bundle
        python={
            "packages": ["zenml", "tensorflow", "Pillow"]
        } # Python package requirements of the model
    )
)
