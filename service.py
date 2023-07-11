import bentoml
from typing import Any
from bentoml.io import Image
import numpy as np
from bentoml.io import Multipart
from bentoml.io import NumpyNdarray
import requests as rq
import tensorflow as tf
from PIL import Image as PILimage
from io import BytesIO

runner = bentoml.tensorflow.get("wf_model:").to_runner()

svc = bentoml.Service(name="wf_service", runners=[runner])


output_spec = NumpyNdarray()
@svc.api(input=NumpyNdarray(dtype="float32"), output=NumpyNdarray())
async def predict(input: NumpyNdarray(dtype="float32")) -> NumpyNdarray():
    url = 'https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/{},{},15,0/350x350'
    access_token = 'pk.eyJ1IjoidGltbGFjaG5lciIsImEiOiJjbGp5MGE0MmcwMGFrM3FsbGFxd2FwMmJvIn0.nP8b9q2owgwoCStcCnGL7Q'
    ending = '&attribution=false&logo=false'
    response = rq.get(url.format(input[0],input[1]) + '?access_token=' + access_token + ending)
    img1= PILimage.open(BytesIO(response.content))
    img_array = tf.keras.utils.img_to_array(img1)
    img_batch = tf.expand_dims(img_array, 0)
    results = runner.predict.run(img_batch)
    return results