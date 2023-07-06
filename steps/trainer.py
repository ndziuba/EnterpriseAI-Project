import tensorflow as tf
import logging
from tensorflow.keras import Sequential
from zenml import pipeline, step
from tensorflow.keras.layers import Flatten
from keras.layers.core import Dense

"""
Train a modified ResNet50 model.
"""
@step
def resnet_trainer(
    train_ds: tf.data.Dataset,
    valid_ds: tf.data.Dataset,
    epochs: int
) -> Sequential:
    model = Sequential()

    # import pretrained model
    resnet_model = tf.keras.applications.ResNet50(
    include_top=False,
    input_shape=(350,350,3),
    pooling='avg',
    weights='imagenet'
    )

    logging.info("Trainer step started")
    # exclude pretrained model weights from being recalculated
    for layer in resnet_model.layers:
        layer.trainable = False

    # add pretrained ResNet50 model to sequential model
    model.add(resnet_model)

    # add additional layers to model
    model.add(Flatten())
    model.add(Dense(512, tf.nn.relu))
    model.add(Dense(2, tf.nn.softmax))
    logging.info("model loading done")
    # train model
    model.compile(optimizer=Adam(), loss='binary_crossentropy', metrics=['accuracy'])
    logging.info("Starting model training")
    model.fit(train_ds, validation_data=valid_ds, epochs=epochs)

    logging.info("Trainer step finished")
    return model