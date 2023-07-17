import tensorflow as tf
import logging
from tensorflow.keras.preprocessing import image_dataset_from_directory
from zenml.integrations.tensorflow.materializers.keras_materializer import KerasMaterializer
from zenml import step
import mlflow

@step(output_materializers=KerasMaterializer, experiment_tracker='mlflow_experiment_tracker') 
def resnet_trainer(model: tf.keras.Model, epochs: int, path: str, batch_size:int) -> tf.keras.Model:
    """
    This function trains a ResNet50 model with modified top layers for a specific task.
    
    Args:
        epochs (int): The number of training epochs.
        path (str): The path to the dataset directory.
        batch_size (int): The batch size used for the training.
        
    Returns:
        model (tf.keras.Model): The trained Keras model.
    """
    logging.info("Loading train and validation data")

    train_ds = image_dataset_from_directory(
        directory = f"{path}/train",
        seed = 1324,
        label_mode = 'categorical',
        image_size = (350, 350),
        batch_size=batch_size
    )

    valid_ds = image_dataset_from_directory(
        directory = f"{path}/valid",
        seed = 1324,
        label_mode = 'categorical',
        image_size = (350, 350),
        batch_size=batch_size
    )

    additional_ds = image_dataset_from_directory(
        directory = path+"/additional",
        seed = 1324,
        label_mode = 'categorical',
        image_size = (350, 350),
        batch_size=batch_size
    )

    # Concatenate a portion of the additional dataset to the test dataset
    train_ds = train_ds.concatenate(additional_ds.take(int(len(additional_ds)*0.6)))

    # Concatenate a portion of the additional dataset to the test dataset
    valid_ds = valid_ds.concatenate(additional_ds.skip(int(len(additional_ds)*0.6)).take(int(len(additional_ds)*0.2)))

    # Apply resizing and rescaling transformations to the dataset
    data_rescale = tf.keras.Sequential([
        tf.keras.layers.Resizing(350, 350),
        tf.keras.layers.Rescaling(1./255)
    ])

    train_ds = train_ds.map(lambda x, y: (data_rescale(x), y))
    valid_ds = valid_ds.map(lambda x, y: (data_rescale(x), y))

    callback = tf.keras.callbacks.EarlyStopping(monitor='loss', patience=2)

    
    mlflow.tensorflow.autolog()  # Ensure MLflow is tracking this model's training
    model.fit(train_ds, validation_data=valid_ds, epochs=epochs, callbacks=[callback])

    return model
