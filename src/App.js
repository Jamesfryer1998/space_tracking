import './App.css';

import { useEffect } from 'react';
import SceneInit from './lib/SceneInit';
import ShapeInit from './lib/ShapeInit';

function App() {
  useEffect(() => {
    const globe_scene = new SceneInit('GlobeCanvas');
    globe_scene.initialize();
    const shape = new ShapeInit(globe_scene.scene)
    shape.createBox(16, 0, 15, 20);
    shape.createSphere(10, 30, -30, -30);
    shape.createSphere(10, -30, -30, -30);
    globe_scene.animate();

  }, []);

  return (
    <div>
      <canvas id='GlobeCanvas'/>
    </div>
  );
}

export default App;