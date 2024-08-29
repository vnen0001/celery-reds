import React from 'react';

import { Navbar, Nav, Container ,Button, NavDropdown} from 'react-bootstrap';
import Home from './components/Home';
import logo from './assets/logo-no-background.png'; // Adjust the path as necessary


function App() {
  

  return (
    <>
     <div className="bg-primary text-white py-2">
        <Container className="d-flex justify-content-start">
          <Button 
            variant="light" 
            href="https://www.petrescue.com.au/" 
            target="_blank" 
            rel="noopener noreferrer"
            
          >
            Adopt a Pet - Find Your New Companion
          </Button>
        </Container>
      </div>
      <Navbar expand="lg" className="navbar-custom">
        <Container>
          <Navbar.Brand href="#home">
            <img
              src={logo}
              width="150"
              height="auto"
              className="d-inline-block align-top"
              alt="Vital Voices Logo"
            />
          </Navbar.Brand>
          <Navbar.Toggle aria-controls="basic-navbar-nav" />
          <Navbar.Collapse id="basic-navbar-nav">
            <Nav className="ml-auto justify-content-between w-100">
              <Nav.Link href="#" className="nav-link-custom">Home</Nav.Link>
              <Nav.Link href="#about" className="nav-link-custom">About</Nav.Link>
              <NavDropdown title="Analysis" id="analysis-dropdown" className="nav-link-custom">
                <NavDropdown.Item href="#gender-disparity" >Gender Disparity</NavDropdown.Item>
                <NavDropdown.Item href="#method-analysis" >Different Methods</NavDropdown.Item>
              </NavDropdown>
              <Nav.Link href="#resources" className="nav-link-custom">Resources</Nav.Link>
            </Nav>
          </Navbar.Collapse>
        </Container>
      </Navbar>
      
      <Home />
    </>
  );
  
}


export default App;
