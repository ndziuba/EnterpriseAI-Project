import type { NextPage } from 'next';
import { ChakraProvider } from '@chakra-ui/react'
import { Formik, Form} from 'formik';
import { Button, FormControl, FormLabel, Input, FormErrorMessage } from "@chakra-ui/react";
import * as Yup from 'yup';
import {
  Container,
  SimpleGrid,
  Flex,
  Heading,
  Text,
  Stack,
  InputGroup,
  InputLeftAddon,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  Divider,
  Image,
  List,
  ListItem,
  ListIcon,
  Box,
  Badge

} from '@chakra-ui/react';
import React, { useState, ChangeEvent } from 'react';
import dynamic from 'next/dynamic';
import { FaLocationArrow } from 'react-icons/fa';
import axios from 'axios';


interface Values {
  lat: number;
  long: number;
}

interface APIResponse {
  success: boolean;
  message: string;
  percentage: number;
  image: string;
}

const validationSchema = Yup.object({
  lat: Yup.number().required('Required'),
  long: Yup.number().required('Required'),
});

const Map = dynamic(() => import('~/components/Map'), { ssr: false });

const Home: NextPage = () => {
  const [lat, setLat] = useState('');
  const [lng, setLng] = useState('');
  const [lastSubmissions, setLastSubmissions] = useState<Values[]>([]);
  const [apiResponse, setAPIResponse] = useState<APIResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);


  const handleLatChange = (event: ChangeEvent<HTMLInputElement>) => {
    const { value } = event.target;
    setLat(value);
  };

  const handleLngChange = (event: ChangeEvent<HTMLInputElement>) => {
    const { value } = event.target;
    setLng(value);
  };

  const initialValues: Values = { lat: 0, long: 0 };

  const handleSubmit = async (values: Values) => {
    setIsLoading(true);
    setError(null);
    try {
      console.log(values);
      setAPIResponse(apiResponse);
  
      setLastSubmissions(prev => [values, ...prev.slice(0, 2)]);
  
      // Fetch satellite image
      let imageBlob;
      try {
        imageBlob = await fetchSatelliteImage(values.lat, values.long);
      } catch (imageFetchError) {
        throw new Error('Failed to fetch image');
      }
  
      // Send image to prediction API
      let predictionResponse;
      try {
        predictionResponse = await sendToPredictAPI(imageBlob);
      } catch (predictionAPIError) {
        // If API gives a 404 error, retry once
        if (axios.isAxiosError(predictionAPIError) && predictionAPIError.response?.status === 404) {
          predictionResponse = await sendToPredictAPI(imageBlob);
        } else {
          throw new Error('Failed to get prediction');
        }
      }
  
      // Update API response state with new prediction
      let wildfire = predictionResponse[0][0] > 0.5 ? false : true;
      let percentage =  wildfire == false ?  (predictionResponse[0][0] * 100).toFixed(2) : (predictionResponse[0][1] * 100).toFixed(2);

      setAPIResponse({
        success: wildfire,
        percentage: +percentage,
        message: wildfire ? 'Potential Wildfire' : 'No Potential Wildfire',
        image: URL.createObjectURL(imageBlob),
      });
  
    } catch (e) {
      setError('Failed to submit coordinates');
    } finally {
      setIsLoading(false);
    }
  };
  
  async function fetchSatelliteImage(lat: number, long: number) {
    let access_token = 'pk.eyJ1IjoidGltbGFjaG5lciIsImEiOiJjbGp5MGE0MmcwMGFrM3FsbGFxd2FwMmJvIn0.nP8b9q2owgwoCStcCnGL7Q';
    const response = await fetch(
      `https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/${long},${lat},15,0/350x350?access_token=${access_token}&attribution=false&logo=false`
    );
    console.log(response);
  
    if (!response.ok) {
      throw new Error('Failed to fetch image');
    }
    
    const blob = await response.blob();
    return blob;
  }
  
  async function sendToPredictAPI(blob: Blob) {
    const formData = new FormData();
    formData.append('image', blob);
  
    const response = await axios.post('https://predict.yatai.k8s.eai.dziubalabs.de/predict_image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  
    if (!response.data) {
      throw new Error('API response error');
    }
  
    return response.data;
  }


  const handleResend = async (values: Values) => {
    setIsLoading(true);
    setError(null);
    console.log('Resending: ' + values.lat + ' ' + values.long);

      let imageBlob;
      try {
        imageBlob = await fetchSatelliteImage(values.lat, values.long);
      } catch (imageFetchError) {
        throw new Error('Failed to fetch image');
      }
  
      // Send image to prediction API
      let predictionResponse;
      try {
        predictionResponse = await sendToPredictAPI(imageBlob);
      } catch (predictionAPIError) {
        // If API gives a 404 error, retry once
        if (axios.isAxiosError(predictionAPIError) && predictionAPIError.response?.status === 404) {
          predictionResponse = await sendToPredictAPI(imageBlob);
        } else {
          throw new Error('Failed to get prediction');
        }
      }
  
      // Update API response state with new prediction
      let wildfire = predictionResponse[0][0] > 0.5 ? false : true;
      let percentage = wildfire == false ? (predictionResponse[0][0] * 100).toFixed(2) : (predictionResponse[0][1] * 100).toFixed(2);
 
      setAPIResponse({
        success: wildfire,
        percentage: +percentage,
        message: wildfire ? 'Potential Wildfire' : 'No Potential Wildfire',
        image: URL.createObjectURL(imageBlob),
      });
  
    };



  return (
    <ChakraProvider>
      <Container maxW={'6xl'} py={12}>
        <SimpleGrid columns={{ base: 1, md: 2 }} spacing={10}>
          <Stack spacing={4}>
            <Heading>Predict the Wildfire on the map.</Heading>
            <Text color={'gray.500'} fontSize={'lg'}>
              You can predict the wildfire on the map by sending coordinates to our machine learning model.
            </Text>

            <Formik initialValues={initialValues} onSubmit={handleSubmit} validationSchema={validationSchema}>
              {(props) => {

                React.useEffect(() => {
                  props.setValues({ lat: parseFloat(lat), long: parseFloat(lng) });
                }, [lat, lng]);

                return (
                  <Form>
                    <SimpleGrid columns={{ base: 1, md: 2 }} spacing={2}>

                      <FormControl mt={4}>
                        <FormLabel>Latitude</FormLabel>
                        <InputGroup>
                          <InputLeftAddon children='Lat:' />
                          <Input
                            name="lat"
                            value={lat}
                            placeholder="Enter latitude"
                            size="md"
                            onChange={(event) => {
                              const { value } = event.target;
                              setLat(value);

                              // Update Formik's state
                              props.setFieldValue('lat', Number(value));
                            }}
                          />
                          <FormErrorMessage>{props.errors.lat}</FormErrorMessage>

                        </InputGroup>

                      </FormControl>

                      <FormControl mt={4}>
                        <FormLabel>Longitude</FormLabel>
                        <InputGroup>
                          <InputLeftAddon children='Long:' />
                          <Input
                            name="lng"
                            value={lng}
                            placeholder="Enter longitude"
                            size="md"
                            onChange={(event) => {
                              const { value } = event.target;
                              setLng(value);

                              // Update Formik's state
                              props.setFieldValue('lng', Number(value));
                            }}
                          />
                          <FormErrorMessage>{props.errors.long}</FormErrorMessage>
                        </InputGroup>
                      </FormControl>
                    </SimpleGrid>


                    <Button
                      mt={4}
                      colorScheme='teal'
                      isLoading={props.isSubmitting}
                      type='submit'
                    >
                      Submit
                    </Button>
                  </Form>
                )
              }}
            </Formik>
            <List>
              {lastSubmissions.map((submission, index) => (
                <ListItem key={index}  mt={2}>
                 <Flex alignItems={'center'}>
                 <ListIcon as={FaLocationArrow} color='green.500' />
                  {submission.lat}, {submission.long}
                  <Button ml={4} size={'xs'} colorScheme='teal' onClick={() => handleResend(submission)}>Resend</Button>
                </Flex>
                </ListItem>
              ))}
            </List>

            <Divider />

            {apiResponse && (

              <Flex margin={2} gap={20} alignItems={'center'} justifyContent={'flex-start'}>
                <Stat width={'max-content'}>
                  <StatLabel><Badge colorScheme='teal'>Prediction</Badge></StatLabel>
                  <StatNumber width={'max-content'}>{apiResponse.message}</StatNumber>
                  <StatHelpText>
                    <Text><StatArrow type={apiResponse.success ? 'increase' : 'decrease'} />Confidence: </Text>
                    <Text as='b'>
                     {apiResponse.percentage}%
                    </Text> 
                  </StatHelpText>
                </Stat>
                <Box width={'max-content'}>
                  <Image maxWidth='400px' width={'100%'} objectFit={'contain'} src={apiResponse.image} alt="API response" />
                </Box>
              </Flex>
            )}

          </Stack>
          <Flex>
            <Map onLatChange={handleLatChange} onLngChange={handleLngChange} />
          </Flex>
        </SimpleGrid>
      </Container>
    </ChakraProvider>

  );
};

export default Home;

