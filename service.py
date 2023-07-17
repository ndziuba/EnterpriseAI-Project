import bentoml
from bentoml.io import NumpyNdarray
from bentoml.io import Image
import tensorflow as tf
from PIL import Image as PILImage
from numpy.typing import NDArray
from typing import Any
import numpy as np
import asyncio

MAX_RETRIES = 3

runner = bentoml.tensorflow.get("wf_model:latest").to_runner()

svc = bentoml.Service(name="wf_service", runners=[runner])


@svc.api(input=Image(), output=NumpyNdarray())
async def predict_image(f: PILImage) -> NDArray[Any]:
    img_tensor  = tf.keras.utils.img_to_array(f)
    img_tensor = img_tensor/255
    
    img_batch = tf.expand_dims(img_tensor , 0)
    

    arr = None  # Default value for arr
    for attempt in range(MAX_RETRIES):
        try:
            arr = await runner.async_run(img_batch)
            break  # If we reach this point, async_run was successful so we break the loop
        except Exception as e:
            if attempt < MAX_RETRIES - 1:  # No need to wait after the last attempt
                wait_time = 1
                print(f"Error: {str(e)}, retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
            else:
                print("Exceeded maximum retries, returning error result...")
                arr = np.array(['Error: Exceeded maximum retries'])

    service_version = svc.__getattribute__('tag').version
    return np.append(arr, service_version)