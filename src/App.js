import './App.css';
import globeImage from '/Users/james/Projects/globe_site/src/lib/img/globe.jpeg'
import NEOImage from '/Users/james/Projects/globe_site/src/lib/img/globe.jpeg'

import { useEffect } from 'react';
import SceneInit from './lib/SceneInit';
import ShapeInit from './lib/ShapeInit';
import DataLoader from './lib/LoadData';
import NEO from './lib/NEOInit';


function App() {
  useEffect(() => {
    // Initialisation of Scene
    const globe_scene = new SceneInit('GlobeCanvas');
    globe_scene.initialize();

    // Creating a Globe (Earth) at the center of the Scene
    const shape = new ShapeInit(globe_scene.scene)
    shape.createSphere(5, 0, 0, 0, globeImage);

    // Loading in NEO data to an array
    const dataLoader = new DataLoader('./src/lib/img/NEO_processed-2023-07-31.json');
    dataLoader.fetchTest();
    // dataLoader.fetchNEOData().then(neoData => {
    //   if (neoData) {
    //     // Create an array to hold NEO instances
    //     const neos = neoData.map(neoItem => {
    //       return new NEO(
    //         neoItem.name || 'Unknown Name',
    //         neoItem['semi_major_axis'] || 0,
    //         neoItem['eccentricity'] || 0,
    //         neoItem['inclination'] || 0,
    //         neoItem['ascending_node_longitude'] || 0,
    //         neoItem['perihelion_distance'] || 0,
    //         neoItem['perihelion_argument'] || 0,
    //         neoItem['mean_anomaly'] || 0,
    //         neoItem['mean_motion'] || 0
    //       );
    //     });
    
    //     // Loop over the NEOs and calculate their positions
    //     neos.forEach(neo => {
    //       const position = neo.calculatePositionAtTime(100);
    //       shape.createSphere(10, 10, 10, 10, globeImage); // This is a test, change back to using the position.
    //     });
    //   } else {
    //     console.error('Error fetching NEO Data. The data is null.');
    //   }
    // });

    // FIXME:
    // - This is not working
    // - Create a logger file and log the creation of each NEO
    // - It may be to to the neoItem['name'] etc instead of using neoItem.name

    // Animate the final scene
    globe_scene.animate();

  }, []);

  return (
    <div>
      <canvas id='GlobeCanvas'/>
    </div>
  );
}

export default App;