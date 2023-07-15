import bentoml
from bentoml.io import NumpyNdarray
from bentoml.io import Image
import tensorflow as tf
from PIL import Image as PILImage
from numpy.typing import NDArray
from typing import Any
import numpy as np


runner = bentoml.tensorflow.get("wf_model:latest").to_runner()

svc = bentoml.Service(name="wf_service", runners=[runner])


@svc.api(input=Image(), output=NumpyNdarray())
async def predict_image(f: PILImage) -> NDArray[Any]:
    img_tensor  = tf.keras.utils.img_to_array(f)
    #img_tensor  = img_tensor  / 255.0
    img_batch = tf.expand_dims(img_tensor , 0)
    
    arr = await runner.async_run(img_batch)

    service_version = svc.__getattribute__('tag').version
    return np.append(arr, service_version)