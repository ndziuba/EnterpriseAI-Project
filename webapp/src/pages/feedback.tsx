import { CheckIcon, CloseIcon } from '@chakra-ui/icons';
import { Box, Heading, Text, HStack, Image } from '@chakra-ui/react';
import { GetServerSideProps } from 'next';

interface FeedbackProps {
    feedback: Array<{
        id: number,
        image: string,
        latitude: number,
        longitude: number,
        prediction: string,
        feedback: number,
        model_version: string
    }>
}

export default function Feedback({ feedback }: FeedbackProps) {
    
    return (
        <HStack spacing={8} flexWrap={'wrap'} justifyContent={'center'} p={'5'}>
            {feedback.map((entry) => (
                <Box key={entry.id} border="1px" borderColor="gray.200" borderRadius="lg" p={4}>
                    <Heading size="md" mb={2}>Feedback #{entry.id}</Heading>
                    <Image maxWidth='300px' width={'100%'} objectFit={'contain'} src={entry.image} alt="API response" />
                    <Text>{entry.latitude}, {entry.longitude}</Text>
                    <Text><strong>Prediction:</strong> {entry.prediction}</Text>
                    <Text><strong>Feedback:</strong> {entry.feedback === 1 ? <CheckIcon /> : <CloseIcon />}</Text>
                    <Text><strong>Model Version:</strong> {entry.model_version}</Text>
                </Box>
            ))}
        </HStack>
    );
}

export const getServerSideProps: GetServerSideProps = async () => {
    try {
        const baseUrl = process.env.NODE_ENV === 'development' ? 'http://localhost:3000' : 'https://eai.dziubalabs.de';
        const res = await fetch(`${baseUrl}/api/getFeedback`);

        if (!res.ok) {
            console.log('Response status:', res.status);
            console.log('Response status text:', res.statusText);
        }

        const feedback = await res.json();

        return {
            props: { feedback },
        };
    } catch (err) {
        console.error('Failed to fetch feedback:', err);
        // return an empty array as a fallback
        return { props: { feedback: [] } };
    }
}