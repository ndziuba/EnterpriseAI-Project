from zenml import step


@step
def deployment_trigger(
    accuracy: float,
    current_accuracy: float,
) -> bool:
    """Implement a simple model deployment trigger.

    The trigger looks at the input model accuracy and decides if it is good
    enough to deploy.

    Args:
        accuracy: The accuracy of the model.
        min_accuracy: The minimum accuracy required to deploy the model.


    Returns:
        True if the model is good enough to deploy, False otherwise.
    """
    return accuracy > current_accuracy