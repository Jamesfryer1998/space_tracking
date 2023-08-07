

export default class NEO {
    constructor(name, semiMajorAxis, eccentricity, inclination, meanAnnomaly,
        acendingNodeLogitude, perihelionDistance, perihelionArgument, meanMotion) {
        this.name = name;
        this.semiMajorAxis = semiMajorAxis;
        this.eccentricity = eccentricity;
        this.inclination = inclination;
        this.meanAnnomaly = meanAnnomaly;
        this.acendingNodeLogitude = acendingNodeLogitude;
        this.perihelionDistance = perihelionDistance;
        this.perihelionArgument = perihelionArgument;
        this.meanMotion = meanMotion;
    }
    
    calculatePositionAtTime(time) {
        // Assuming time is in days since the NEO's last perihelion passage
        const meanAnomalyAtTime = this.meanAnomaly + this.meanMotion * time;
        const eccentricAnomaly = this.calculateEccentricAnomaly(meanAnomalyAtTime);
      
        // Calculate heliocentric distance
        const r = this.semiMajorAxis * (1 - this.eccentricity * Math.cos(eccentricAnomaly));
      
        // Calculate x, y, z coordinates in the orbital plane
        const xOrbital = r * Math.cos(eccentricAnomaly);
        const yOrbital = r * Math.sin(eccentricAnomaly);
        const zOrbital = 0; // Assuming the orbital plane is the xy-plane for simplicity
      
        // Rotate the coordinates to account for inclination and ascending node longitude
        const x = xOrbital * Math.cos(this.ascendingNodeLongitude) - yOrbital * Math.sin(this.ascendingNodeLongitude);
        const y = xOrbital * Math.sin(this.ascendingNodeLongitude) + yOrbital * Math.cos(this.ascendingNodeLongitude);
        const z = zOrbital * Math.sin(this.inclination);
      
        return { x, y, z };
      }
      
      calculateEccentricAnomaly(meanAnomaly) {
        // Use Newton-Raphson iteration to find the eccentric anomaly
        let eccentricAnomaly = meanAnomaly; // Initial guess
        const tolerance = 1e-8; // Set a tolerance for convergence
      
        for (let i = 0; i < 15; i++) {
          const nextAnomaly = eccentricAnomaly - (eccentricAnomaly - this.eccentricity * Math.sin(eccentricAnomaly) - meanAnomaly) / (1 - this.eccentricity * Math.cos(eccentricAnomaly));
          if (Math.abs(nextAnomaly - eccentricAnomaly) < tolerance) {
            eccentricAnomaly = nextAnomaly;
            break;
          }
          eccentricAnomaly = nextAnomaly;
        }
      
        return eccentricAnomaly;
      }
}