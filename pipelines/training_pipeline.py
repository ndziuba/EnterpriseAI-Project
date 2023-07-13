from zenml import pipeline
import bentoml
#from zenml.config import DockerSettings
from zenml.integrations.constants import TENSORFLOW
from steps import (
    evaluator,
    hp_trainer,
    data_loader,
    discord_bot,
    trigger_decision,
    bento_builder
)


#docker_settings = DockerSettings(required_integrations=[TENSORFLOW])
#@pipeline(enable_cache=False, settings={"docker": docker_settings})

@pipeline(enable_cache=False)
def training_pipeline(path: str='data', batch_size: int = 32 , epochs: int = 5):
    """Train, evaluate, and deploy a model."""
    new_count = data_loader.data_loader()
    model = hp_trainer.resnet_hp_trainer(path=path, batch_size=batch_size, epochs = epochs)
    model_eval = evaluator.model_evaluator(model)

    current_model = bentoml.keras.load_model("wf_model:latest")
    current_eval = evaluator.model_evaluator(current_model)
    decision = trigger_decision.trigger_decision(model_eval, current_eval)
    if(decision):
        bento_builder.bento_builder(model=model)
    discord_bot.discord_alert(decision)
