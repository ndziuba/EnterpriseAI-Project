import axios from 'axios';
import { NextApiRequest, NextApiResponse } from 'next';
import FormData from 'form-data';
import intoStream from 'into-stream';

export default async function handleRequest(req: NextApiRequest, res: NextApiResponse) {
  const { lat, long } = req.body;

  // Fetch satellite image
  let access_token = 'pk.eyJ1IjoidGltbGFjaG5lciIsImEiOiJjbGp5MGE0MmcwMGFrM3FsbGFxd2FwMmJvIn0.nP8b9q2owgwoCStcCnGL7Q';
  const imageResponse = await axios.get(
    `https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/${long},${lat},15,0/350x350?access_token=${access_token}&attribution=false&logo=false`,
    { responseType: 'arraybuffer' }
  );

  if (imageResponse.status !== 200) {
    res.status(500).json({ error: 'Failed to fetch image' });
    return;
  }

  const imageStream = intoStream(imageResponse.data);

  // Create form-data and append the image
  const formData = new FormData();
  formData.append('image', imageStream, 'image.jpeg');

  // Send image to prediction API
  const predictResponse = await axios.post(
    'https://predict.yatai.k8s.eai.dziubalabs.de/predict_image', 
    formData, 
    {
      headers: {
        ...formData.getHeaders(),
      },
    }
  );

  if (!predictResponse.data) {
    res.status(500).json({ error: 'API response error' });
    return;
  }

  let predictionResponse = predictResponse.data;

  // Update API response state with new prediction
  let wildfire = predictionResponse[0] > 0.5 ? false : true;
  let percentage =  wildfire == false ?  (predictionResponse[0] * 100).toFixed(2) : (predictionResponse[1] * 100).toFixed(2);
  let modelVersion = predictionResponse[2];
  const base64Image = Buffer.from(imageResponse.data, 'binary').toString('base64');
  console.log(`Wildfire: ${wildfire}, Percentage: ${percentage}, Model Version: ${modelVersion}, Latitude: ${lat}, Longitude: ${long}`);
  res.status(200).json({
    success: wildfire,
    latitude: lat,
    longitude: long,
    percentage: +percentage,
    message: wildfire ? 'Wildfire potential' : 'No Wildfire potential',
    image: `data:image/jpeg;base64,${base64Image}`,  // return as data URL
    modelVersion: modelVersion,
  });
}
