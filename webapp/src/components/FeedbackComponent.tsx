import React, { useState } from 'react';
import axios from 'axios';
import { VStack, HStack, Alert, AlertIcon, Text, AlertDescription, Button } from '@chakra-ui/react';
import { CheckIcon, CloseIcon } from '@chakra-ui/icons';

interface Feedback {
    image: string;
    latitude: number;
    longitude: number;
    prediction: string;
    feedback: boolean | null;
    modelVersion: string;
}

const FeedbackComponent: React.FC<Feedback> = ({ image, latitude, longitude, prediction, modelVersion }) => {
    const [isLoading, setIsLoading] = useState(false);
    const [isSubmitted, setIsSubmitted] = useState(false);

    const handleFeedback = async (isPositive: boolean) => {
        setIsLoading(true);
        try {
            await axios.post('/api/handleFeedback', {
                image: image,
                latitude: latitude,
                longitude: longitude,
                prediction: prediction,
                feedback: isPositive,
                modelVersion: modelVersion,
            });
            setIsSubmitted(true);
        } catch (error) {
            console.error('Failed to send feedback', error);
        } finally {
            setIsLoading(false);
        }
    };

    if (isSubmitted) {
        return (
            <VStack width={'100%'} alignItems={'flex-start'}>
                <Alert
                    status='success'
                    variant='subtle'
                    width='max-content'
                    >
                    <AlertIcon boxSize='20px' mr={2} />
                    <AlertDescription maxWidth='sm'>
                        Feedback submitted!
                    </AlertDescription>
                </Alert>
            </VStack>
        );
    }

    return (
        <VStack width={'100%'} alignItems={'flex-start'}>
            <Text fontSize={'12px'} >Was our prediction accurate?</Text>
            <HStack width={'100%'}>
                <Button mr={2} size={'xs'} leftIcon={<CheckIcon />} colorScheme="green" isLoading={isLoading} onClick={() => handleFeedback(true)}>
                    Yes
                </Button>
                <Button mr={2} size={'xs'} leftIcon={<CloseIcon />} colorScheme="red" isLoading={isLoading} onClick={() => handleFeedback(false)}>
                    No
                </Button>
            </HStack>
        </VStack>
    );
};

export default FeedbackComponent;
