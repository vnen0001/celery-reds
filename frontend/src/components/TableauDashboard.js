import React, { useEffect } from 'react';

function TableauDashboard() {
  useEffect(() => {
    const initViz = () => {
      const vizContainer = document.getElementById('vizContainer');
      const url = 'https://public.tableau.com/views/MethodsofSuicide/Dashboard1?:language=en-US&:embed=true&publish=yes&:redirect=auth';
      const options = {
        hideTabs: true,
        width: '100%',
        height: '100%',
        onFirstInteractive: function () {
          console.log('Tableau Viz has finished loading.');
        }
      };
      new window.tableau.Viz(vizContainer, url, options);
    };

    // Load Tableau's JavaScript API
    const script = document.createElement('script');
    script.src = 'https://public.tableau.com/javascripts/api/viz_v1.js';
    script.onload = initViz;
    document.body.appendChild(script);
  }, []);

  return (
    <div id="vizContainer" style={{ width: '100%', height: '800px' }}></div>
  );
}

export default TableauDashboard;
