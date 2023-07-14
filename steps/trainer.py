import tensorflow as tf
import logging
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Flatten, Dense
from tensorflow.keras.preprocessing import image_dataset_from_directory
from tensorflow.keras.optimizers import Adam
from zenml.integrations.tensorflow.materializers.keras_materializer import KerasMaterializer
import mlflow

@step(output_materializers=KerasMaterializer, experiment_tracker='mlflow_experiment_tracker', enable_cache=True) 
def resnet_trainer(epochs: int, path: str, batch_size:int) -> tf.keras.Model:
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

    logging.info("Setting up the model architecture")

    model = Sequential()
    resnet_model = tf.keras.applications.ResNet50(
        include_top=False,
        input_shape=(350,350,3),
        pooling='avg',
        weights='imagenet'
    )
    for layer in resnet_model.layers:
        layer.trainable = False

    model.add(resnet_model)
    model.add(Flatten())
    model.add(Dense(256, activation=tf.nn.relu))
    model.add(Dense(2, activation=tf.nn.softmax))

    logging.info("Starting model training")

    model.compile(optimizer=Adam(), loss='binary_crossentropy', metrics=['accuracy'])
    mlflow.tensorflow.autolog()  # Ensure MLflow is tracking this model's training
    model.fit(train_ds, validation_data=valid_ds, epochs=epochs)

    return model
