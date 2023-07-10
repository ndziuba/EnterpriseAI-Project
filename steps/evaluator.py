import tensorflow as tf
import logging
from tensorflow.keras import Sequential
from zenml import step
from zenml.steps import Output
from tensorflow.keras.preprocessing import image_dataset_from_directory
"""
Validate the trained model.
"""

@step(enable_cache=False, experiment_tracker='mlflow_experiment_tracker') 
def model_evaluator(model: tf.keras.Model, path: str='data', batch_size: int = 32) -> Output(
    test_acc=float,
    additional_acc=float):
    logging.info("Evaluator step started")
    # returns list with loss and accuracy
    logging.info("Loading test data")
    test_ds = image_dataset_from_directory(
        directory = "data/test",
        seed = 1324,
        label_mode = 'categorical',
        image_size = (350, 350),
        batch_size=32
    )
    
    additional_ds = image_dataset_from_directory(
        directory = "data/additional",
        seed = 1324,
        label_mode = 'categorical',
        image_size = (350, 350),
        batch_size=32
    )
    test_acc = model.evaluate(test_ds)
    additional_acc = model.evaluate(additional_ds.skip(int(len(additional_ds)*0.8)))
    print(f"Test accuracy: {test_acc} Additional accuracy: {additional_acc}")
    logging.info("Evaluator step finished")
    return test_acc[1], additional_acc[1]