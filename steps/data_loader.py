
import tensorflow as tf
from tensorflow.python.lib.io import file_io
from tensorflow.keras.preprocessing import image_dataset_from_directory
from tensorflow.image import stateless_random_flip_left_right
import logging
from zenml import pipeline, step
from zenml.steps import Output
from typing import Type
from zenml.materializers.base_materializer import BaseMaterializer
from zenml.enums import ArtifactType
import os

class TensorFlowDatasetMaterializer(BaseMaterializer):
    ASSOCIATED_TYPES = (tf.data.Dataset,)
    ASSOCIATED_ARTIFACT_TYPE = ArtifactType.DATA

    def load(self, data_type: Type[tf.data.Dataset]) -> tf.data.Dataset:
        """Read from artifact store."""
        return tf.data.experimental.load(self.uri)

    def save(self, dataset: tf.data.Dataset) -> None:
        """Write to artifact store."""
        tf.data.experimental.save(dataset, self.uri)


"""
Import the data using tf.image_dataset_from_directory.
"""
@step(enable_cache=False, output_materializers=TensorFlowDatasetMaterializer)
def data_loader(path: str='data', batch_size: int=32) -> Output(
    train_ds=tf.data.Dataset,
    valid_ds=tf.data.Dataset,
    test_ds=tf.data.Dataset,
    ):
    logging.info("Loading raw data")
    train_ds = image_dataset_from_directory(
        directory = path+"/train",
        seed = 1324,
        label_mode = 'categorical',
        image_size = (350, 350),
        batch_size=None
    )  
    valid_ds = image_dataset_from_directory(
        directory = path+"/valid",
        seed = 1324,
        label_mode = 'categorical',
        image_size = (350, 350),
        batch_size=None
    )
    test_ds = image_dataset_from_directory(
        directory = path+"/test",
        seed = 1324,
        label_mode = 'categorical',
        image_size = (350, 350),
        batch_size=None
    )
    
    additional_ds = image_dataset_from_directory(
        directory = path+"/additional",
        seed = 1324,
        label_mode = 'categorical',
        image_size = (350, 350),
        batch_size=None
    )
    logging.info("Divide additional data")
    train_ds = train_ds.concatenate(additional_ds.take(int(len(additional_ds)*0.6)))
    valid_ds = valid_ds.concatenate(additional_ds.skip(int(len(additional_ds)*0.6))
                                     .take(int(len(additional_ds)*0.2)))
    test_ds = test_ds.concatenate(additional_ds.skip(int(len(additional_ds)*0.6))
                                   .skip(int(len(additional_ds)*0.2))
                                   .take(int(len(additional_ds)*0.2)))
    # logging.info("Apply augmentation")
    # train_ds = train_ds.map(
    #                  lambda image, label: (stateless_random_flip_left_right(image, seed=(1, 2)) if label[1] == 1 else image, label)
    #            )
    # valid_ds = valid_ds.map(
    #                  lambda image, label: (stateless_random_flip_left_right(image, seed=(1, 2)) if label[1] == 1 else image, label)
    #            )
    # valid_ds = valid_ds.map(
    #                  lambda image, label: (stateless_random_flip_left_right(image, seed=(1, 2)) if label[1] == 1 else image, label)
    #          )
    
    logging.info("Batching")
    train_ds = train_ds.batch(batch_size)
    valid_ds = valid_ds.batch(batch_size)
    test_ds = test_ds.batch(batch_size)
    logging.info("DATA LOADER DONE")
    return train_ds, valid_ds, test_ds
