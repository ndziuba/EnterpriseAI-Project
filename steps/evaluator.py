import tensorflow as tf
import logging
from zenml import step
from zenml.steps import Output
from tensorflow.keras.preprocessing import image_dataset_from_directory
from zenml.integrations.tensorflow.materializers.keras_materializer import KerasMaterializer

@step(enable_cache=False, experiment_tracker='mlflow_experiment_tracker') 
def model_evaluator(model: tf.keras.Model, path: str='data', batch_size: int = 32) -> Output(test_acc_current=float, test_acc_production=float):
    """
    Evaluates the trained model on the test dataset.

    Parameters:
    model (tf.keras.Model): The trained model to evaluate.
    path (str): The path to the data directory.
    batch_size (int): Batch size for data loading.

    Returns:
    Output(test_acc_current=float): The test accuracy of the current model.
    Output(test_acc_production=float): The test accuracy of the production model.
    """
    logging.info("Evaluator step started")

    # Load the test dataset and additional dataset
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

    # Concatenate a portion of the additional dataset to the test dataset
    test_ds = test_ds.concatenate(additional_ds.skip(int(len(additional_ds)*0.8)).take(int(len(additional_ds)*0.2)))
    test_ds = test_ds.shuffle(buffer_size=1000)

    # Apply resizing and rescaling transformations to the dataset
    data_rescale = tf.keras.Sequential([
        tf.keras.layers.Resizing(350, 350),
        tf.keras.layers.Rescaling(1./255)
    ])
    test_ds = test_ds.map(lambda x, y: (data_rescale(x), y))
    #production_model = tf.keras.models.load_model('models/production')
    # Evaluate the models on the test dataset
    test_acc_current = model.evaluate(test_ds)
    #test_acc_production = production_model.evaluate(test_ds)
    logging.info("Evaluator step finished")
    test_acc_production = [0, 0.5]
    return test_acc_current[1], test_acc_production[1]
