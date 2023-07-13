from zenml import pipeline
import bentoml
import os
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
def training_pipeline(path: str='data', batch_size: int = 32 , epochs: int = 1):
    """Train, evaluate, and deploy a model."""
    new_count = data_loader.data_loader()
    model = hp_trainer.resnet_hp_trainer(path=path, batch_size=batch_size, epochs = epochs)
    model_eval = evaluator.model_evaluator(model)

    #current_model = bentoml.tensorflow.get("wf_model:latest")
    #current_eval = evaluator.model_evaluator(current_model)
    decision = trigger_decision.deployment_trigger(model_eval, 0.9)

    if(decision):
        print('test')
        bento_builder.bento_builder(model=model)
        os.popen("bentoml cloud login --api-token ${APITOKEN} --endpoint https://yatai.k8s.eai.dziubalabs.de/")
        os.popen("bentoml push wf_service:latest")
    #discord_bot.discord_alert(decision)