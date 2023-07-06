from zenml import pipeline
#from zenml.config import DockerSettings
from zenml.integrations.constants import TENSORFLOW


from steps import (
    evaluator,
    trainer,
    data_loader
)


#docker_settings = DockerSettings(required_integrations=[TENSORFLOW])
#@pipeline(enable_cache=False, settings={"docker": docker_settings})

@pipeline(enable_cache=False)

def training_pipeline(path: str='data', batch_size: int = 32 , epochs: int = 5):
    """Train, evaluate, and deploy a model."""
    train_ds, valid_ds, test_ds = data_loader.data_loader(path=path, batch_size=batch_size)
    model = trainer.resnet_trainer(train_ds=train_ds, valid_ds=valid_ds, epochs=epochs)
    evaluator.model_evaluator(test_ds=test_ds, model=model)
