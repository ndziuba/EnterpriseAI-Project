import tensorflow as tf
from tensorflow.keras import Sequential
from zenml import step
from zenml.steps import Output


"""

Compress the trained model.

"""

@step(enable_cache=False, experiment_tracker='mlflow_experiment_tracker') 
def model_evaluator(model: tf.keras.Model, path: str='data', batch_size: int = 32) -> tf.keras.Model:
    model_compressed = model
    return model_compressed