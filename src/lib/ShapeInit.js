import * as THREE from 'three';
// import image from '/Users/james/Projects/globe_site/src/lib/img/globe.jpeg'
// Change this to '/Users/james/Projects/globe_site/src/lib/img/earth_16k.jpeg' in production


export default class ShapeInit {
    constructor(scene) {
        // Core components to build a shape
        this.scene = scene
        this.shape = undefined;
    }

    // Create a box with a defined size and position
    createBox(size, x=0, y=0, z=0) {
        const boxGeometry = new THREE.BoxGeometry(size, size, size);
        const boxMaterial = new THREE.MeshNormalMaterial();
        const boxMesh = new THREE.Mesh(boxGeometry, boxMaterial);
        this.scene.add(boxMesh);
        this.setShapePosition(boxMesh, x, y, z);
    }

    // Create a sphere with a defined size and position
    createSphere(size, x = 0, y = 0, z = 0, image) {
        const sphereGeometry = new THREE.SphereGeometry(size, 50, 50);
        const textureLoader = new THREE.TextureLoader();
        const texture = textureLoader.load(image);
        const sphereMaterial = new THREE.MeshStandardMaterial({ map: texture });
        const sphereMesh = new THREE.Mesh(sphereGeometry, sphereMaterial);
        this.scene.add(sphereMesh);
        this.setShapePosition(sphereMesh, x, y, z);
    }

    // Set the position of the shape on the scene
    setShapePosition(shape, x=0, y=0, z=0) {
        shape.position.set(x, y, z)
        // shape.rotation.x += 0.008;
        shape.rotation.y -= 0.00015; // -= Spinning Clockwise
        shape.rotation.z -= 0.000015; // -= Spinning Clockwise
        requestAnimationFrame(() => this.setShapePosition(shape, x, y, z));
    }
}