import tensorflow as tf
import logging
import os
from zenml import step
from tensorflow.keras.preprocessing import image_dataset_from_directory
from zenml.integrations.tensorflow.materializers.keras_materializer import KerasMaterializer

@step(enable_cache=False)
def deployer(model: tf.keras.Model, decision: bool, path=''):
    """
    This function checks if a decision is made to save the current model and then saves it if it is.
    If the decision is True, it also pushes the current state of the model to a remote BentoML repository.

    Args:
        model (tf.keras.Model): The model to be saved.
        decision (bool): The decision whether to save the model or not.
        path (str): The directory path where the model will be saved.

    Returns:
        None
    """
    # if decision is True, log into BentoML and push the current state of the model
    if decision:
        os.popen("bentoml cloud login --api-token ${APITOKEN} --endpoint https://yatai.k8s.eai.dziubalabs.de/")
        os.popen("bentoml push wf_service:latest")
        # save the current model in the specified path
        model.save(os.path.join(path, 'models', 'production'))