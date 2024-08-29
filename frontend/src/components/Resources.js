import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Container, ListGroup, ListGroupItem } from 'react-bootstrap';

const Resources = () => {
  const [resources, setResources] = useState([]);

  useEffect(() => {
    axios.get('/api/resources/')
      .then(response => {
        setResources(response.data);
      })
      .catch(error => {
        console.error('Error fetching resources:', error);
      });
  }, []);

  return (
    <Container>
      <h1 className="my-4">Resources</h1>
      <ListGroup>
        {resources.map(resource => (
          <ListGroupItem key={resource.id}>
            <h2>{resource.title}</h2>
            <p>{resource.content}</p>
            {resource.link && <a href={resource.link} target="_blank" rel="noopener noreferrer">Learn more</a>}
          </ListGroupItem>
        ))}
      </ListGroup>
    </Container>
  );
};

export default Resources;
