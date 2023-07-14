from zenml import pipeline
from steps import (
    discord_bot,
    evaluator,
    trainer,
    data_loader,
    trigger_decision,
    bento_builder,
    deployer,
    hp_tuner
)

@pipeline(enable_cache=True)
def training_pipeline(path: str='data', batch_size: int = 32 , epochs: int = 5, hp_tuning_epochs: int = 2):
    """Main pipeline to train, evaluate, and deploy a model.

    Args:
        path (str): Path to the directory containing the training data.
        batch_size (int): Batch size for training.
        epochs (int): Number of epochs for training.
    """

    new_count = data_loader.data_loader()

    optimal_model = hp_tuner.hp_tuner(epochs=hp_tuning_epochs, path=path, batch_size=batch_size)

    trained_model = trainer.resnet_trainer(model=optimal_model, path=path, batch_size=batch_size, epochs = epochs)

    bento_builder.bento_builder(model=trained_model)

    #test_acc_current, test_acc_production = evaluator.model_evaluator(trained_model)

    #decision = trigger_decision.deployment_trigger(test_acc_current, test_acc_production)    
    
    #deployer.deployer(trained_model, decision)
    
    #discord_bot.discord_alert(decision, test_acc_current)
