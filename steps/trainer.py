import tensorflow as tf
import logging
from tensorflow.keras import Sequential
from zenml import step
from tensorflow.keras.layers import Flatten
from keras.layers.core import Dense
from tensorflow.keras.preprocessing import image_dataset_from_directory
from tensorflow.keras.optimizers import Adam
from zenml.integrations.tensorflow.materializers.keras_materializer import KerasMaterializer
import mlflow

"""
Train a modified ResNet50 model.
"""
@step(output_materializers=KerasMaterializer, experiment_tracker='mlflow_experiment_tracker') 
def resnet_trainer(epochs: int, path: str, batch_size:int
) -> tf.keras.Model:
    logging.info("Loading train/valid/additional data")
    train_ds = image_dataset_from_directory(
        directory = path+"/train",
        seed = 1324,
        label_mode = 'categorical',
        image_size = (350, 350),
        batch_size=batch_size
    )  
    valid_ds = image_dataset_from_directory(
        directory = path+"/valid",
        seed = 1324,
        label_mode = 'categorical',
        image_size = (350, 350),
        batch_size=batch_size
    )

    """
    additional_ds = image_dataset_from_directory(
        directory = path+"/additional",
        seed = 1324,
        label_mode = 'categorical',
        image_size = (350, 350),
        batch_size=batch_size
    )
    
    train_ds = train_ds.concatenate(additional_ds.take(int(len(additional_ds)*0.6)))
    valid_ds = valid_ds.concatenate(additional_ds.skip(int(len(additional_ds)*0.6))
                                     .take(int(len(additional_ds)*0.2)))
    """
    model = Sequential()

    # import pretrained model
    resnet_model = tf.keras.applications.ResNet50(
    include_top=False,
    input_shape=(350,350,3),
    pooling='avg',
    weights='imagenet'
    )

    # exclude pretrained model weights from being recalculated
    for layer in resnet_model.layers:
        layer.trainable = False

    # add pretrained ResNet50 model to sequential model
    model.add(resnet_model)

    # add additional layers to model
    model.add(Flatten())
    model.add(Dense(512, tf.nn.relu))
    model.add(Dense(2, tf.nn.softmax))
    
    # train model
    model.compile(optimizer=Adam(), loss='binary_crossentropy', metrics=['accuracy'])
    mlflow.tensorflow.autolog()
    model.fit(train_ds, validation_data=valid_ds, epochs=epochs)

    return model