import tensorflow as tf
from tensorflow.keras import Sequential
from zenml import pipeline, step
from tensorflow.keras.layers import Flatten
from keras.layers.core import Dense

"""
Validate the trained model.
"""
@step
def model_evaluator(
    train_ds: tf.data.Dataset,
    model: Sequential()
) -> float:
    # returns list with loss and accuracy
    test_acc = model.evaluate()
    
    test_acc = test_acc[1]
    print(f"Test accuracy: {test_acc}")
    return test_acc