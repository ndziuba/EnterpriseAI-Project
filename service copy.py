import bentoml
from typing import Any
from bentoml.io import Image
import numpy as np
from bentoml.io import Multipart
from bentoml.io import NumpyNdarray
import requests as rq
import tensorflow as tf
from PIL import Image
from io import BytesIO

runner = bentoml.keras.get(MODEL_NAME).to_runner()

svc = bentoml.Service(name=SERVICE_NAME, runners=[runner])

def interpolate_images(baseline,
                       image,
                       alphas):
  alphas_x = alphas[:, tf.newaxis, tf.newaxis, tf.newaxis]
  baseline_x = tf.expand_dims(baseline, axis=0)
  input_x = tf.expand_dims(image, axis=0)
  delta = input_x - baseline_x
  images = baseline_x +  alphas_x * delta
  return images

def compute_gradients(images, target_class_idx):
  with tf.GradientTape() as tape:
    tape.watch(images)
    logits = runner.run(images)
    probs = tf.nn.softmax(logits, axis=-1)[:, target_class_idx]
  return tape.gradient(probs, images)

def integral_approximation(gradients):
  # riemann_trapezoidal
  grads = (gradients[:-1] + gradients[1:]) / tf.constant(2.0)
  integrated_gradients = tf.math.reduce_mean(grads, axis=0)
  return integrated_gradients

@tf.function
def one_batch(baseline, image, alpha_batch, target_class_idx):
    # Generate interpolated inputs between baseline and input.
    interpolated_path_input_batch = interpolate_images(baseline=baseline,
                                                       image=image,
                                                       alphas=alpha_batch)

    # Compute gradients between model outputs and interpolated inputs.
    gradient_batch = compute_gradients(images=interpolated_path_input_batch,
                                       target_class_idx=target_class_idx)
    return gradient_batch

def integrated_gradients(baseline,
                         image,
                         target_class_idx,
                         m_steps=30,
                         batch_size=32):
  # Generate alphas.
  alphas = tf.linspace(start=0.0, stop=1.0, num=m_steps+1)

  # Collect gradients.    
  gradient_batches = []

  # Iterate alphas range and batch computation for speed, memory efficiency, and scaling to larger m_steps.
  for alpha in tf.range(0, len(alphas), batch_size):
    from_ = alpha
    to = tf.minimum(from_ + batch_size, len(alphas))
    alpha_batch = alphas[from_:to]

    gradient_batch = one_batch(baseline, image, alpha_batch, target_class_idx)
    gradient_batches.append(gradient_batch)

  # Concatenate path gradients together row-wise into single tensor.
  total_gradients = tf.concat(gradient_batches, axis=0)

  # Integral approximation through averaging gradients.
  avg_gradients = integral_approximation(gradients=total_gradients)

  # Scale integrated gradients with respect to input.
  integrated_gradients = (image - baseline) * avg_gradients

  return integrated_gradients



output_spec = Multipart(output=Image(), result=NumpyNdarray(), eai=Tensor())
@svc.api(input=NumpyNdarray(dtype="float32"), output=NumpyNdarray())
async def predict(input: NumpyNdarray(dtype="float32")) -> PILImage | NumpyNdarray() | Tensor():
    url = 'https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/{},{},15,0/350x350'
    access_token = 'pk.eyJ1IjoidGltbGFjaG5lciIsImEiOiJjbGp5MGE0MmcwMGFrM3FsbGFxd2FwMmJvIn0.nP8b9q2owgwoCStcCnGL7Q'
    ending = '&attribution=false&logo=false'
    response = rq.get(url.format(input[0],inout[1]) + '?access_token=' + access_token + ending)
    img1= Image.open(BytesIO(response.content))
    img_array = tf.keras.utils.img_to_array(img1)
    img_batch = tf.expand_dims(img_array, 0)
    prediction = runner.async_run(img_batch)
    attributions = integrated_gradients(baseline=tf.zeros(shape=(350,350,3)),
                                      image=img_array,
                                      target_class_idx=prediction,
                                      m_steps=30)
    attribution_mask = tf.reduce_sum(tf.math.abs(attributions), axis=-1)
    return await img1, prediction, attribution_mask