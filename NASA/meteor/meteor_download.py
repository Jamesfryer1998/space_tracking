import os
import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime
import time
import math


class AsteroidData:
    def __init__(self, url, api_key_path, save_file_path, processed_file_path):
        self.url = url
        self.date_now = datetime.now()
        self.save_file_path = f'{save_file_path}-{self.date_now.date()}.json'
        self.processed_file_path = f'{processed_file_path}-{self.date_now.date()}.json'
        self.api_key = self.load_json(api_key_path)["api_key"]
        self.request_url = f'{self.url}{self.api_key}'

    def check_file_exists(self, file_path):
        return os.path.exists(file_path)
    
    def load_json(self, file_path):
        with open(file_path, 'r') as infile:
            data = json.load(infile)
        return data

    def save_data(self, data, file_path):
        with open(file_path, 'w') as outfile:
            json.dump(data, outfile, indent=3)

    def file_stats(self, data):
        neo_data = data["near_earth_objects"]
        dates = sorted(neo_data.keys())
        self.all_neos = [neo_data[date][index] for date in dates for index in range(len(neo_data[date]))]
        
        print('=== File Stats ===')
        print(f'Dates of NEOs: {dates}')
        print(f'Total Num NEOs: {len(self.all_neos)}')
        
        close_approach_data = [neo["close_approach_data"][0] for neo in self.all_neos]
        relative_velocities = np.array([float(data["relative_velocity"]["miles_per_hour"]) for data in close_approach_data])
        miss_distances = np.array([float(data["miss_distance"]["kilometers"]) for data in close_approach_data])
        estimated_diameter_min = [neo["estimated_diameter"]["kilometers"]["estimated_diameter_min"] for neo in self.all_neos]
        estimated_diameter_max = [neo["estimated_diameter"]["kilometers"]["estimated_diameter_max"] for neo in self.all_neos]
        
        print(f'All Orbiting Bodies: {set(data["orbiting_body"] for data in close_approach_data)}')
        print(f'AVG mph of NEO: {np.mean(relative_velocities)}')
        print(f'AVG kph of NEO: {np.mean(relative_velocities * 1.60934)}')
        print(f'AVG kps of NEO: {np.mean(relative_velocities * 1.60934) / 60 / 60}')
        print(f'Closest Asteroid (kilometers): {np.min(miss_distances)}')
        print(f'Furthest Asteroid (kilometers): {np.max(miss_distances)}')
        print(f'Biggest Asteroid (kilometers): {np.min(estimated_diameter_min)}')
        print(f'Smallest Asteroid (kilometers): {np.max(estimated_diameter_max)}')
        print('==================')

    def get_raw_data(self):
        if not self.check_file_exists(self.save_file_path):
            print(f'Saving file to: {self.save_file_path}\n')
            response = requests.get(self.request_url)
            self.raw_data = response.json()
            self.save_data(self.raw_data, self.save_file_path)
            self.file_stats(self.raw_data)
        else:
            print(f'Loading file from: {self.save_file_path}\n')
            self.raw_data = self.load_json(self.save_file_path)
            self.file_stats(self.raw_data)

    def get_asteroid_data_by_id(self, asteroid_id):
        response = requests.get(f'https://api.nasa.gov/neo/rest/v1/neo/{asteroid_id}?api_key={self.api_key}')
        raw_data = response.json()
        time.sleep(1)
        return raw_data["orbital_data"]
    
    def process_data(self):
        processed_data = []
        if not self.check_file_exists(self.processed_file_path):
            for asteroid, index in zip(self.all_neos, range(len(self.all_neos))):
                print(f'Processing Asteroid {asteroid["name"]} - {asteroid["id"]}... {index+1}/{len(self.all_neos)}')
                ast_data = self.get_asteroid_data_by_id(asteroid['id'])
                ast_dict = {
                    "id": asteroid['id'], # ID of NEO
                    "name": asteroid['name'], # Name of NEO
                    "velocity": asteroid['close_approach_data'][0]['relative_velocity'], # Speed of NEO
                    "miss_distance": asteroid['close_approach_data'][0]['miss_distance'], # Distance NEO missed Earth
                    "ODD": ast_data['orbit_determination_date'], # (Orbit Determination Data) When Orbit was determined
                    "epoch_osculation": ast_data['epoch_osculation'], # Reference epoch for orbital elements (When orbit was determined)
                    "eccentricity": ast_data['eccentricity'], # Shape of NEO orbit
                    "semi_major_axis": ast_data['semi_major_axis'],  # AVG distance form center of orbit to NEO
                    "inclination": ast_data['inclination'], # Angle between the orbital plan and equator
                    "ascending_node_longitude": ast_data['ascending_node_longitude'], # Longitude of ascending point, where the orbit intersects the referenve plane
                    "perihelion_distance": ast_data['perihelion_distance'], # Closest distance between NEO and suns orbit
                    "perihelion_argument": ast_data['perihelion_argument'], # Angle between perihelion and ascending node
                    "aphelion_distance": ast_data['aphelion_distance'], # The farthest distance betweem NEO and suns orbit
                    "mean_anomaly": ast_data['mean_anomaly'], # Fraction of orbit period elapsed since reference epoch
                    "mean_motion": ast_data['mean_motion'] # AVG angular speed at which NEO moves along its orbit
                }
                neo_position, neo_velocity = self.track_neo_position(ast_dict)
                print(f"NEO Position: {neo_position}")
                print(f"NEO Velocity: {neo_velocity}")

                processed_data.append(ast_dict)
                print(f'Completed Asteroid {asteroid["name"]} - {asteroid["id"]}\n')

            self.save_data({"NEO_data":processed_data}, self.processed_file_path)

        else:
            print(f'All NEOs processed for {self.date_now.date()}')
        
    # Will need to change this to be consistent with the size of the THREE globe
    ##############################################
    
    def convert_deg_to_rad(self, degrees):
        return math.radians(float(degrees))

    def convert_km_to_au(self, kilometers):
        return float(kilometers) / 149597870.7

    def calculate_position_velocity(self,semi_major_axis, eccentricity, inclination, ascending_node_longitude,
                                perihelion_argument, true_anomaly):
        eccentricity = float(eccentricity)
        # Convert orbital elements to radians
        inclination_rad = self.convert_deg_to_rad(inclination)
        ascending_node_longitude_rad = self.convert_deg_to_rad(ascending_node_longitude)
        perihelion_argument_rad = self.convert_deg_to_rad(perihelion_argument)
        true_anomaly_rad = self.convert_deg_to_rad(true_anomaly)

        # Calculate position and velocity in 3D space
        x = semi_major_axis * (math.cos(true_anomaly_rad) - eccentricity)
        y = semi_major_axis * math.sqrt(1 - eccentricity**2) * math.sin(true_anomaly_rad)
        z = 0.0

        v_x = -math.sqrt((1 + eccentricity) / (semi_major_axis * (1 - eccentricity))) * math.sin(true_anomaly_rad)
        v_y = math.sqrt((1 + eccentricity) / (semi_major_axis * (1 - eccentricity))) * math.cos(true_anomaly_rad)
        v_z = 0.0

        # Apply rotations to position and velocity vectors
        x_prime = x * (math.cos(ascending_node_longitude_rad) * math.cos(perihelion_argument_rad) -
                    math.sin(ascending_node_longitude_rad) * math.sin(perihelion_argument_rad) *
                    math.cos(inclination_rad)) - \
                y * (math.sin(ascending_node_longitude_rad) * math.cos(perihelion_argument_rad) +
                    math.cos(ascending_node_longitude_rad) * math.sin(perihelion_argument_rad) *
                    math.cos(inclination_rad))
        y_prime = x * (math.cos(ascending_node_longitude_rad) * math.sin(perihelion_argument_rad) +
                    math.sin(ascending_node_longitude_rad) * math.cos(perihelion_argument_rad) *
                    math.cos(inclination_rad)) + \
                y * (math.cos(ascending_node_longitude_rad) * math.cos(perihelion_argument_rad) -
                    math.sin(ascending_node_longitude_rad) * math.sin(perihelion_argument_rad) *
                    math.cos(inclination_rad))
        z_prime = x * (math.sin(ascending_node_longitude_rad) * math.sin(inclination_rad)) + \
                y * (math.cos(ascending_node_longitude_rad) * math.sin(inclination_rad))

        v_x_prime = v_x * (math.cos(ascending_node_longitude_rad) * math.cos(perihelion_argument_rad) -
                    math.sin(ascending_node_longitude_rad) * math.sin(perihelion_argument_rad) *
                    math.cos(inclination_rad)) - \
                v_y * (math.sin(ascending_node_longitude_rad) * math.cos(perihelion_argument_rad) +
                    math.cos(ascending_node_longitude_rad) * math.sin(perihelion_argument_rad) *
                    math.cos(inclination_rad))
        v_y_prime = v_x * (math.cos(ascending_node_longitude_rad) * math.sin(perihelion_argument_rad) +
                    math.sin(ascending_node_longitude_rad) * math.cos(perihelion_argument_rad) *
                    math.cos(inclination_rad)) + \
                v_y * (math.cos(ascending_node_longitude_rad) * math.cos(perihelion_argument_rad) -
                    math.sin(ascending_node_longitude_rad) * math.sin(perihelion_argument_rad) *
                    math.cos(inclination_rad))
        v_z_prime = v_x * (math.sin(ascending_node_longitude_rad) * math.sin(inclination_rad)) + \
                v_y * (math.cos(ascending_node_longitude_rad) * math.sin(inclination_rad))

        return (x_prime, y_prime, z_prime), (v_x_prime, v_y_prime, v_z_prime)

    def calculate_true_anomaly(self, mean_anomaly, eccentricity):
        eccentric_anomaly = self.mean_anomaly_to_eccentric_anomaly(mean_anomaly, eccentricity)
        true_anomaly = self.eccentric_anomaly_to_true_anomaly(eccentric_anomaly, eccentricity)
        return true_anomaly

    def mean_anomaly_to_eccentric_anomaly(self, mean_anomaly, eccentricity):
        E0 = mean_anomaly  # Initial guess for eccentric anomaly

        # # Iterate to improve the estimate of eccentric anomaly
        # while True:
        #     E1 = E0 - (E0 - eccentricity * math.sin(E0) - mean_anomaly) / (1 - eccentricity * math.cos(E0))
        #     if abs(E1 - E0) < 1e-8:
        #         break
        #     E0 = E1

        return E0

    def eccentric_anomaly_to_true_anomaly(self, eccentric_anomaly, eccentricity):
        true_anomaly = 2 * math.atan2(math.sqrt(1 + float(eccentricity)) * math.sin(float(eccentric_anomaly) / 2),
                                    math.sqrt(1 - float(eccentricity)) * math.cos(float(eccentric_anomaly) / 2))
        return math.degrees(true_anomaly)

    # Example usage
    def track_neo_position(self, ast_dict):
        semi_major_axis = self.convert_km_to_au(ast_dict['semi_major_axis'])
        eccentricity = ast_dict['eccentricity']
        inclination = ast_dict['inclination']
        ascending_node_longitude = ast_dict['ascending_node_longitude']
        perihelion_argument = ast_dict['perihelion_argument']
        mean_anomaly = ast_dict['mean_anomaly']

        true_anomaly = self.calculate_true_anomaly(mean_anomaly, eccentricity)
        position, velocity = self.calculate_position_velocity(semi_major_axis, eccentricity, inclination,
                                                        ascending_node_longitude, perihelion_argument, true_anomaly)

        # You can now use the calculated position and velocity to track the NEO at the given time

        return position, velocity

    ##############################################
    
    def run_asteroid_data(self):
        self.get_raw_data()
        self.process_data()

AsteroidData(url="https://api.nasa.gov/neo/rest/v1/feed?api_key=",
             api_key_path="NASA/api_key.json", 
             save_file_path="NASA/meteor/Cache/raw/NEO_raw",
             processed_file_path="NASA/meteor/Cache/processed/NEO_processed"
             ).run_asteroid_data()