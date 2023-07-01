from zenml import pipeline, step
from zenml.steps import Output
from tensorflow.keras.preprocessing import image_dataset_from_directory
from tensorflow.image import stateless_random_flip_left_right
import tensorflow as tf
import logging
"""
Import the data using tf.image_dataset_from_directory.
"""
@step()
def data_loader(path:str) -> Output(
    train_ds=tf.data.Dataset,
    valid_ds=tf.data.Dataset,
    test_ds=tf.data.Dataset,
    additional_ds=tf.data.Dataset,
    ):
    logging.info("Loading raw data")
    train_ds = image_dataset_from_directory(
        directory = path+"/train",
        seed = 1324,
        label_mode = 'categorical',
        image_size = (350, 350)
    )  
    valid_ds = image_dataset_from_directory(
        directory = path+"/valid",
        seed = 1324,
        label_mode = 'categorical',
        image_size = (350, 350)
    )
    test_ds = image_dataset_from_directory(
        directory = path+"/test",
        seed = 1324,
        label_mode = 'categorical',
        image_size = (350, 350)
    )
    additional_ds = image_dataset_from_directory(
        directory = path+"/additional",
        seed = 1324,
        label_mode = 'categorical',
        image_size = (350, 350)
    )
    return train_ds, valid_ds, test_ds, additional_ds

# @step 
# def data_validator(train_ds=tf.data.Dataset,
#     valid_ds=tf.data.Dataset,
#     test_ds=tf.data.Dataset,
#     additional_ds=tf.data.Dataset) -> Output(train_ds=tf.data.Dataset,
#     valid_ds=tf.data.Dataset,
#     test_ds=tf.data.Dataset,):
#     return train_ds, valid_ds, test_ds
"""
Divides the content of additional_ds over the train, valid, test ds.
"""
@step
def add_additional(train_ds=tf.data.Dataset,
    valid_ds=tf.data.Dataset,
    test_ds=tf.data.Dataset,
    additional_ds=tf.data.Dataset) -> Output(train_ds=tf.data.Dataset,
    valid_ds=tf.data.Dataset,
    test_ds=tf.data.Dataset,):
    logging.info("Divide additional data")
    train_ds = train_ds.concatenate(additional_ds.take(int(len(additional_ds)*0.6)))
    valid_ds = valid_ds.concatenate(additional_ds.skip(int(len(additional_ds)*0.6))
                                    .take(int(len(additional_ds)*0.2)))
    test_ds = test_ds.concatenate(additional_ds.skip(int(len(additional_ds)*0.6))
                                  .skip(int(len(additional_ds)*0.2))
                                  .take(int(len(additional_ds)*0.2)))
    return train_ds, valid_ds, test_ds
"""
Applys the tf.image.stateless_random_flip_left_right transformation to wildifre examples


"""
@step
def data_augmentor(train_ds=tf.data.Dataset,
    valid_ds=tf.data.Dataset,
    test_ds=tf.data.Dataset) -> Output(train_ds=tf.data.Dataset,
    valid_ds=tf.data.Dataset,
    test_ds=tf.data.Dataset,
    ):
    logging.info("Apply augmentation")
    train_ds = train_ds.map(
                    lambda image, label: (stateless_random_flip_left_right(image, seed=(1, 2)) if label[1] == 1 else image, label)
              )
    valid_ds = valid_ds.map(
                    lambda image, label: (stateless_random_flip_left_right(image, seed=(1, 2)) if label[1] == 1 else image, label)
              )
    valid_ds = valid_ds.map(
                    lambda image, label: (stateless_random_flip_left_right(image, seed=(1, 2)) if label[1] == 1 else image, label)
              )
    return train_ds, valid_ds, test_ds

@step
def data_batcher(train_ds=tf.data.Dataset,
    valid_ds=tf.data.Dataset,
    test_ds=tf.data.Dataset, batch_size=int) -> Output(train_ds=tf.data.Dataset,
    valid_ds=tf.data.Dataset,
    test_ds=tf.data.Dataset,
    ):
    logging.info("Batch")
    return train_ds.batch(batch_size), valid_ds.batch(batch_size), test_ds.batch(batch_size)


@pipeline()
def first_pipeline():
    train_ds, valid_ds, test_ds, additional_ds = data_loader("data")
    train_ds, valid_ds, test_ds = add_additional(train_ds, valid_ds, test_ds, additional_ds)
    train_ds, valid_ds, test_ds = data_augmentor(train_ds, valid_ds, test_ds)
    train_ds, valid_ds, test_ds = data_batcher(train_ds, valid_ds, test_ds, 32)
if __name__ == "__main__":
    first_pipeline()