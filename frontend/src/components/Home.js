


import React, { useEffect, useState } from 'react';
import { Container, Row, Col, Card } from 'react-bootstrap';
import { TableauEmbed } from "@stoddabr/react-tableau-embed-live";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';
import supportImage from '../assets/people-meeting-support-group.jpg';
import infographic from '../assets/infographic.jpg';

const Home = () => {
  const [articles] = useState([
    {
      title: "Understanding Male Mental Health",
      excerpt: "Explore the unique challenges men face in addressing mental health issues...",
      link: "https://mensline.org.au/mens-mental-health/mens-mental-health-common-challenges/#:~:text=Some%20men%20may%20be%20more,it%20in%20a%20healthy%20way."
    },
    {
      title: "Breaking the Stigma: Men and Therapy",
      excerpt: "Discover how therapy can be a powerful tool for men's mental well-being...",
      link: "https://www.butler.org/blog/breaking-the-stigma-of-mens-mental-health"
    },
    {
      title: "Mindfulness Techniques for Stress Reduction",
      excerpt: "Learn practical mindfulness exercises tailored for men to manage stress...",
      link: "https://www.mindful.org/how-to-manage-stress-with-mindfulness-and-meditation/"
    }
  ]);

  const resources = [
    {
      title: "Healthdirect",
      subtitle: "Dads in Distress",
      phone: "1300 853 437",
      link: "https://www.healthdirect.gov.au/"
    },
    {
      title: "Mensline",
      phone: "1300 78 99 78",
      link: "https://mensline.org.au/"
    },
    {
      title: "Men's Shed",
      phone: "1300 550 009",
      link: "https://mensshed.org/"
    }
  ];

  const [data, setData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeLine, setActiveLine] = useState(null);
  const [spiderData, setSpiderData] = useState({ maleData: [], femaleData: [] });
  const [activeGender, setActiveGender] = useState(null);

  const processData = (rawData) => {
    const femaleData = rawData.find(item => item.year === "Females");
    const maleData = rawData.find(item => item.year === "Males");

    const years = Object.keys(femaleData).filter(key => !isNaN(parseInt(key)));

    return years.map(year => ({
      year: parseInt(year),
      Female: femaleData[year],
      Male: maleData[year]
    })).sort((a, b) => a.year - b.year);
  };

  const processSpiderData = (rawData) => {
    const maleData = [];
    const femaleData = [];

    rawData.forEach(item => {
      const chartItem = {
        subject: item.Agegroup.length > 30 ? item.Agegroup.substring(0, 30) + '...' : item.Agegroup,
        A: item.total_count,
        fullMark: Math.max(...rawData.map(d => d.total_count))
      };

      if (item.Sex === 'Males') {
        maleData.push(chartItem);
      } else if (item.Sex === 'Females') {
        femaleData.push(chartItem);
      }
    });

    return { maleData, femaleData };
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('/api/graph/');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const result = await response.json();

        const processedData = processData(result);
        setData(processedData);
        setIsLoading(false);
      } catch (error) {
        console.error('Error fetching data:', error);
        setError(error.message);
        setIsLoading(false);
      }
    };

    const fetchSpiderData = async () => {
      try {
        const response = await fetch('/api/spider/');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const result = await response.json();

        const processedData = processSpiderData(result);
        setSpiderData(processedData);
      } catch (error) {
        console.error('Error fetching spider chart data:', error);
      }
    };

    fetchData();
    fetchSpiderData();
  }, []);

  const handleLegendClick = (dataKey) => {
    if (activeLine === dataKey) {
      setActiveLine(null);
      setActiveGender(dataKey);
    } else {
      setActiveLine(dataKey);
      setActiveGender(dataKey);
    }
  };

  const renderSpiderChart = (data, title) => (
    <div style={{ width: '100%', height: 400 }}>
      <ResponsiveContainer>
        <RadarChart outerRadius="80%" data={data}>
          <PolarGrid />
          <PolarAngleAxis dataKey="subject" />
          <PolarRadiusAxis angle={30} domain={[0, 'auto']} />
          <Radar name={title} dataKey="A" stroke={title === 'Males' ? "#0000FF" : "#FF69B4"}
            fill={title === 'Males' ? "#0000FF" : "#FF69B4"} />
          <Tooltip />
          <Legend />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <>
      <Container fluid className="px-0">
        {/* Hero Section */}
        <section className="hero-section text-center text-white d-flex align-items-center justify-content-center" style={{
          backgroundImage: `linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)), url(${supportImage})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          height: '100vh'
        }}>
          <div>
            <h1 className="display-3 fw-bold mb-4" style={{ color: '#f8f4eb' }}>
              In 2022, <span style={{ color: '#ff5a3c', fontSize: '1.2em' }}>2455</span> men took their own lives in Australia
            </h1>
            <p className="lead fs-2 mb-5" style={{ color: '#f8f4eb' }}>How can we take this number to 0?</p>
            <a href="#gender-disparity" className="btn btn-primary btn-lg">Learn More</a>
          </div>
        </section>

        <Container className="py-5">
          

          {/* Gender Disparity Section */}
          <section id="gender-disparity" className="my-5">
            <h2 className="text-center mb-5 section-header" style={{ fontSize: '2.5em', padding: '10px' }}>Gender Disparity in Suicide Rates</h2>
            <p className="text-center mb-4">The graph below illustrates the stark difference in suicide rates between males and females from 1907 to 2022. Click on a legend item to highlight that data series.</p>
            <div style={{ width: '100%', height: 400 }}>
              <ResponsiveContainer>
                <LineChart
                  data={data}
                  margin={{
                    top: 5,
                    right: 30,
                    left: 20,
                    bottom: 5,
                  }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="year"
                    label={{ value: 'Year', position: 'bottom', offset: 0 }}
                  />
                  <YAxis
                    label={{ value: 'Number of Suicides', angle: -90, position: 'insideLeft' }}
                  />
                  <Tooltip />
                  <Legend onClick={(e) => handleLegendClick(e.dataKey)} />
                  <Line
                    type="monotone"
                    dataKey="Male"
                    stroke="#0000FF"
                    activeDot={{ r: 8 }}
                    strokeWidth={activeLine === 'Male' ? 4 : 2}
                    opacity={activeLine && activeLine !== 'Male' ? 0.3 : 1}
                  />
                  <Line
                    type="monotone"
                    dataKey="Female"
                    stroke="#FF69B4"
                    activeDot={{ r: 8 }}
                    strokeWidth={activeLine === 'Female' ? 4 : 2}
                    opacity={activeLine && activeLine !== 'Female' ? 0.3 : 1}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
            <p className="mt-4">
              This graph clearly shows the historical trend of suicide rates for males and females from 1907 to 2022.
              The x-axis represents the years, while the y-axis shows the number of suicides.
              Consistently across this period, males have had higher suicide rates compared to females.
              This long-term data highlights the persistent nature of the gender disparity in suicide rates,
              emphasizing the critical need for targeted interventions and support systems.
            </p>
          </section>
          {activeGender && (
            <section id="top-mechanisms" className="my-5">
              <h2 className="text-center mb-5 section-header" style={{ fontSize: '2.5em', padding: '10px' }}>Self harm in Age Group for {activeGender}s</h2>
              <p className="text-center mb-4">This spider web chart shows the different age group for {activeGender.toLowerCase()}s across 2008 to 2022.</p>
              {renderSpiderChart(activeGender === 'Male' ? spiderData.maleData : spiderData.femaleData, activeGender)}
              <p className="mt-4 text-center">
                This spider web chart illustrates the relative disparity of {activeGender.toLowerCase()}s across all recorded years in terms of self and different methods of self harm.
                The chart's scale is based on the total count of incidents for each age group.
                The men in the age group of 25 -44 have made more attempts and are more prone to perform self harm compaared to females.This is main reason our target audience is set to 25 -44 years.
              </p>
            </section>
          )}

          {/* Analysis Section */}
          <section id="method-analysis" className="my-5">
            <h2 className="text-center mb-5 section-header" style={{ fontSize: '2.5em', padding: '10px' }}>Analysis</h2>
            <p className="text-center mb-4">Explore our interactive dashboard for detailed data how different methods are used for suicide by Men.</p>
            <div className="tableau-container">
              <TableauEmbed
                sourceUrl='https://public.tableau.com/views/MethodsofSuicide/Dashboard1?:language=en-US&:sid=&:redirect=auth&:display_count=n&:origin=viz_share_link'
                style={{ height: '800px', width: '100%' }}
                toolbar="hidden"
              />
            </div>
          </section>
          {/* About Section */}
          <section id="about" className="my-5">
            <h2 className="text-center mb-5 section-header" style={{ fontSize: '2.5em', padding: '10px' }}>About Us</h2>
            <Row className="align-items-center">
              <Col md={6}>
                <p className="lead">
                  Despite growing awareness of mental health issues, Australian men aged 25-65 continue to face significant barriers in seeking help. We're here to change that.
                </p>
                <p>
                  Our mission is to provide innovative, accessible, and male-friendly solutions that address these barriers and empower men to seek help, ultimately reducing suicide rates and promoting overall well-being.
                </p>
              </Col>
              <Col md={6}>
                <img
                  src={infographic}
                  alt="Infographic"
                  className="img-fluid rounded shadow-lg"
                />
              </Col>
            </Row>
          </section>

          {/* Articles Section */}
          <section id="articles" className="my-5">
            <h2 className="text-center mb-5 section-header" style={{ fontSize: '2.5em', padding: '10px' }}>Latest Articles</h2>
            <Row>
              {articles.map((article, index) => (
                <Col md={4} key={index} className="mb-4">
                  <Card className="h-100 shadow-sm hover-card">
                    <Card.Body>
                      <Card.Title>{article.title}</Card.Title>
                      <Card.Text>{article.excerpt}</Card.Text>
                      <a href={article.link} className="btn btn-primary" target="_blank" rel="noopener noreferrer">Read More</a>
                    </Card.Body>
                  </Card>
                </Col>
              ))}
            </Row>
          </section>

          {/* Resources Section */}
          <section id="resources" className="my-5">
            <h2 className="text-center mb-5 section-header" style={{ fontSize: '2.5em', padding: '10px' }}>Resources</h2>
            <p className="text-center mb-4">If you are a man experiencing mental health issues, Pleas see some resources below:</p>
            <Row>
              {resources.map((resource, index) => (
                <Col md={4} key={index} className="mb-4">
                  <Card className="h-100 shadow-sm hover-card">
                    <Card.Body className="d-flex flex-column justify-content-center align-items-center text-center">
                      <Card.Title className="mb-3">
                        <a href={resource.link} target="_blank" rel="noopener noreferrer" className="text-dark text-decoration-none">
                          {resource.title}
                        </a>
                      </Card.Title>
                      {resource.subtitle && <Card.Subtitle className="mb-2 text-muted">{resource.subtitle}</Card.Subtitle>}
                      <Card.Text className="fs-4 fw-bold text-primary">
                        <a href={`tel:${resource.phone}`} className="text-primary text-decoration-none">{resource.phone}</a>
                      </Card.Text>
                    </Card.Body>
                  </Card>
                </Col>
              ))}
            </Row>
          </section>
        </Container>
      </Container>
    </>
  );
};

export default Home;
