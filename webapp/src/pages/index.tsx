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
  Badge,
  VStack,
  IconButton

} from '@chakra-ui/react';
import React, { useState, ChangeEvent } from 'react';
import dynamic from 'next/dynamic';
import { FaLocationArrow, FaRegCommentAlt } from 'react-icons/fa';
import FeedbackComponent from '../components/FeedbackComponent';
import { useRouter } from 'next/router';



interface Values {
  lat: number;
  long: number;
}

interface APIResponse {
  latitude: number;
  longitude: number;
  success: boolean;
  message: string;
  percentage: number;
  image: string;
  modelVersion: string;
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
      const response = await fetch('/api/handlePrediction', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(values)
      });
  
      if (!response.ok) {
        throw new Error('Failed to submit coordinates');
      }
  
      const apiResponse = await response.json();
  
      setAPIResponse(apiResponse);
      setLastSubmissions(prev => [values, ...prev.slice(0, 2)]);
      
    } catch (e) {
      if (e instanceof Error) {
        setError(e.message);
      } else {
        setError('An unknown error occurred');
      }
    } finally {
      setIsLoading(false);
      setIsSubmitted(false);
    }
  };
  

  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleResend = async (values: Values) => {
    setIsLoading(true);
    setError(null);
    console.log('Resending: ' + values.lat + ' ' + values.long);

    try {
      const response = await fetch('/api/handlePrediction', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(values)
      });
  
      if (!response.ok) {
        throw new Error('Failed to submit coordinates');
      }
  
      const apiResponse = await response.json();
  
      setAPIResponse(apiResponse);
      
    } catch (e) {
      if (e instanceof Error) {
        setError(e.message);
      } else {
        setError('An unknown error occurred');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const router = useRouter();

  const handleFeedbackClick = () => {
    router.push("/feedback");
  }

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
              <Flex margin={2} gap={20} alignItems={'left'} justifyContent={'flex-start'}>
                <VStack justifyContent={'center'}>
                <Stat width={'max-content'} height={'max-content'} flexGrow={'0'}>
                  <StatLabel><Badge colorScheme='teal'>Prediction</Badge></StatLabel>
                  <StatNumber width={'max-content'}>{apiResponse.message}</StatNumber>
                  <StatHelpText>
                    <Text><StatArrow type={apiResponse.success ? 'increase' : 'decrease'} />Confidence: </Text>
                    <Text as='b'>
                     {apiResponse.percentage}%
                    </Text> 
                  </StatHelpText>
                </Stat>
                <FeedbackComponent 
                image={apiResponse.image}
                feedback={null}
                latitude={apiResponse.latitude}
                longitude={apiResponse.longitude}
                prediction={apiResponse.message}
                modelVersion={apiResponse.modelVersion}
                isSubmitted={isSubmitted}
                setIsSubmitted={setIsSubmitted}
              />
              </VStack>
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
      <Box position="fixed" right="2rem" bottom="2rem">
        <IconButton
          colorScheme="teal"
          aria-label="Send feedback"
          icon={<FaRegCommentAlt />}
          onClick={handleFeedbackClick}
        />
      </Box>
    </ChakraProvider>

  );
};

export default Home;


