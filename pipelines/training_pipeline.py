from zenml import pipeline
from steps import (
    discord_bot,
    evaluator,
    hp_trainer,
    data_loader,
    trigger_decision,
    bento_builder,
    deployer
)

@pipeline(enable_cache=False)
def training_pipeline(path: str='data', batch_size: int = 32 , epochs: int = 1):
    """Main pipeline to train, evaluate, and deploy a model.

    Args:
        path (str): Path to the directory containing the training data.
        batch_size (int): Batch size for training.
        epochs (int): Number of epochs for training.
    """
    new_count = data_loader.data_loader()
    model = hp_trainer.resnet_hp_trainer(path=path, batch_size=batch_size, epochs = epochs)
    test_acc_current, test_acc_production = evaluator.model_evaluator(model)
    decision = trigger_decision.deployment_trigger(test_acc_current, test_acc_production)    
    bento_builder.bento_builder(model=model)
    deployer.deployer(model, decision)
    discord_bot.discord_alert(decision)
