import tensorflow as tf
import logging
from tensorflow.keras import Sequential
from zenml import step
from steps.data_loader import TensorFlowDatasetMaterializer

"""
Validate the trained model.
"""
@step(enable_cache=False, output_materializers=TensorFlowDatasetMaterializer)
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