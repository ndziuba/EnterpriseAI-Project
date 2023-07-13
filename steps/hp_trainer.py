import logging
import mlflow
from zenml import step
import tensorflow as tf
from tensorflow.keras.preprocessing import image_dataset_from_directory
from zenml.integrations.tensorflow.materializers.keras_materializer import KerasMaterializer
import keras_tuner as kt




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
        units=hp.Choice("units", values=[128, 265,512]),
        activation= tf.nn.relu,
        )
    )


    model.add(tf.keras.layers.Dense(2, tf.nn.softmax))
    model.compile(optimizer=tf.keras.optimizers.Adam(), loss='binary_crossentropy', metrics=['accuracy'])
    
    return model

"""
Train a modified ResNet50 model.
"""
@step(output_materializers=KerasMaterializer, experiment_tracker='mlflow_experiment_tracker') 
def resnet_hp_trainer(epochs: int, path: str, batch_size:int
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

    additional_ds = image_dataset_from_directory(
        directory = path+"/additional",
        seed = 1324,
        label_mode = 'categorical',
        image_size = (350, 350),
        batch_size=batch_size
    )

    data_augmentation = tf.keras.Sequential([
        tf.keras.layers.RandomFlip("horizontal_and_vertical")])

    train_ds = train_ds.map(lambda x, y: (data_augmentation(x, training=True), y))
    valid_ds = valid_ds.map(lambda x, y: (data_augmentation(x, training=True), y))


    train_ds = train_ds.concatenate(additional_ds.take(int(len(additional_ds)*0.6)))
    valid_ds = valid_ds.concatenate(additional_ds.skip(int(len(additional_ds)*0.6))
                                     .take(int(len(additional_ds)*0.2)))
    train_ds = train_ds.shuffle(buffer_size=1000)
    valid_ds = valid_ds.shuffle(buffer_size=1000)
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
        max_trials=20)
    
    tuner.search(train_ds, epochs=5, validation_data=(valid_ds))

    model = tuner.get_best_models()[0]
    mlflow.tensorflow.autolog()
    model.fit(train_ds, validation_data=valid_ds, epochs=epochs)

    return model