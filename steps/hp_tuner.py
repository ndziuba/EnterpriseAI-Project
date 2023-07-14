import tensorflow as tf
import keras_tuner as kt
import logging
from zenml import step
from zenml.steps import Output
from tensorflow.keras.preprocessing import image_dataset_from_directory
from zenml.integrations.tensorflow.materializers.keras_materializer import KerasMaterializer

def build_model(hp):
    # initialize model
    model = tf.keras.Sequential()

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
    model.add(tf.keras.layers.Flatten())

    model.add(tf.keras.layers.Dense(
       # Tune number of units.
        units=hp.Choice("units", values=[128, 256, 512]),
        activation= tf.nn.relu,
        )
    )

    model.add(tf.keras.layers.Dense(2, tf.nn.softmax))
    model.compile(optimizer=tf.keras.optimizers.Adam(), loss='binary_crossentropy', metrics=['accuracy'])
    
    return model




@step(experiment_tracker='mlflow_experiment_tracker', output_materializers=KerasMaterializer, enable_cache=True) 
def hp_tuner(epochs: int, path: str, batch_size:int) -> tf.keras.Model:

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

    additional_ds = image_dataset_from_directory(
        directory = path+"/additional",
        seed = 1324,
        label_mode = 'categorical',
        image_size = (350, 350),
        batch_size=batch_size
    )

    # Concatenate a portion of the additional dataset to the test dataset
    train_ds = train_ds.concatenate(additional_ds.take(int(len(additional_ds)*0.6)))
    #train_ds = train_ds.shuffle(buffer_size=1000)

    # Concatenate a portion of the additional dataset to the test dataset
    valid_ds = valid_ds.concatenate(additional_ds.skip(int(len(additional_ds)*0.6)).take(int(len(additional_ds)*0.2)))
    #valid_ds = valid_ds.shuffle(buffer_size=1000)

    # Apply resizing and rescaling transformations to the dataset
    data_rescale = tf.keras.Sequential([
        tf.keras.layers.Resizing(350, 350),
        tf.keras.layers.Rescaling(1./255)
    ])
    
    train_ds = train_ds.map(lambda x, y: (data_rescale(x), y))
    valid_ds = valid_ds.map(lambda x, y: (data_rescale(x), y))


    tuner = kt.RandomSearch(
        build_model,
        objective='val_accuracy',
        seed=1234,
        overwrite=True,
        max_trials=20,
        directory='models/hp_tuning')
    
    tuner.search(train_ds, epochs=epochs, validation_data=(valid_ds))

    return tuner.get_best_models()[0]