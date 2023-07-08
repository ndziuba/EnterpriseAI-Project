from zenml import pipeline
#from zenml.config import DockerSettings
from zenml.integrations.constants import TENSORFLOW
from steps import (
    evaluator,
    trainer
)


#docker_settings = DockerSettings(required_integrations=[TENSORFLOW])
#@pipeline(enable_cache=False, settings={"docker": docker_settings})

@pipeline(enable_cache=False)
def training_pipeline(path: str='data', batch_size: int = 32 , epochs: int = 5):
    """Train, evaluate, and deploy a model."""
    model = trainer.resnet_trainer(1, path, batch_size)
    evaluator.model_evaluator(model, path, batch_size )
