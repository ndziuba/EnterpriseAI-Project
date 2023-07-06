import tensorflow as tf
import logging
from tensorflow.keras import Sequential
from zenml import pipeline, step
from tensorflow.keras.layers import Flatten
from keras.layers.core import Dense

"""
Validate the trained model.
"""
@step
def model_evaluator(
    test_ds: tf.data.Dataset,
    model: Sequential()
) -> float:
    logging.info("Evaluator step started")
    # returns list with loss and accuracy
    test_acc = model.evaluate(test_ds)
    
    test_acc = test_acc[1]
    print(f"Test accuracy: {test_acc}")
    logging.info("Evaluator step finished")
    return test_acc