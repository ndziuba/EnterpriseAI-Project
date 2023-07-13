import tensorflow as tf
import logging
from zenml import step
from zenml.steps import Output
from tensorflow.keras.preprocessing import image_dataset_from_directory
"""
Validate the trained model.
"""

@step(enable_cache=False, experiment_tracker='mlflow_experiment_tracker') 
def model_evaluator(model: tf.keras.Model, path: str='data', batch_size: int = 32) -> Output(
    test_acc=float,
    #additional_acc=float
    ):
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
        directory = path+"/additional",
        seed = 1324,
        label_mode = 'categorical',
        image_size = (350, 350),
        batch_size=batch_size
    )
    test_ds = test_ds.concatenate(additional_ds.skip(int(len(additional_ds)*0.8))
                                     .take(int(len(additional_ds)*0.2)))
    test_ds = test_ds.shuffle(buffer_size=1000)

    data_rescale = tf.keras.Sequential([
        tf.keras.layers.Resizing(350, 350),
        tf.keras.layers.Rescaling(1./255)
    ])

    test_ds = test_ds.map(lambda x, y: (data_rescale(x), y))


    test_acc = model.evaluate(test_ds)
    logging.info("Evaluator step finished")
    return test_acc[1]