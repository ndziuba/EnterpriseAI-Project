from zenml import pipeline
import os
import bentoml
#from zenml.config import DockerSettings
from zenml.integrations.constants import TENSORFLOW
from steps import (
    evaluator,
    trainer,
    bento_builder
)


#docker_settings = DockerSettings(required_integrations=[TENSORFLOW])
#@pipeline(enable_cache=False, settings={"docker": docker_settings})

@pipeline(enable_cache=True)
def bentoml_pipeline(path: str='data', batch_size: int = 32 , epochs: int = 5):
    """Train, evaluate, and deploy a model."""
    model = trainer.resnet_trainer(1, path, batch_size)
    #accuracy = evaluator.model_evaluator(model, path, batch_size )
    bento = bento_builder.bento_builder(model=model)


#os.popen("bentoml cloud login --api-token ${APITOKEN} --endpoint https://yatai.k8s.eai.dziubalabs.de/")
#os.popen("bentoml push  wildfire:latest")