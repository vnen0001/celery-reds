import React from 'react';
import { Container, Card } from 'react-bootstrap';

const About = () => {
  return (
    <Container>
      <Card className="text-center my-4">
        <Card.Body>
          <Card.Title>About Vital Voices</Card.Title>
          <Card.Text>
            Vital Voices is dedicated to raising awareness and providing support for men's mental health and suicide prevention in Australia.
          </Card.Text>
          <Card.Text>
            We believe that by providing access to resources and fostering community support, we can make a difference in the lives of men struggling with mental health issues.
          </Card.Text>
        </Card.Body>
      </Card>
    </Container>
  );
};

export default About;
