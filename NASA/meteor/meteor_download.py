import os
import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime
import time

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
        
        # asterdoid_ids = [neo["neo_reference_id"] for neo in self.all_neos]
        close_approach_data = [neo["close_approach_data"][0] for neo in self.all_neos]
        relative_velocities = np.array([float(data["relative_velocity"]["miles_per_hour"]) for data in close_approach_data])
        miss_distances = np.array([float(data["miss_distance"]["kilometers"]) for data in close_approach_data])
        estimated_diameter_min = [neo["estimated_diameter"]["kilometers"]["estimated_diameter_min"] for neo in self.all_neos]
        estimated_diameter_max = [neo["estimated_diameter"]["kilometers"]["estimated_diameter_max"] for neo in self.all_neos]
        
        print(f'All Orbiting Bodies: {set(data["orbiting_body"] for data in close_approach_data)}')
        print(f'AVG mph of NEO: {np.mean(relative_velocities)}')
        print(f'AVG kph of NEO: {np.mean(relative_velocities * 1.60934)}')
        print(f'AVG kps of NEO: {np.mean(relative_velocities * 0.44704)}')
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
        else:
            print(f'Loading file from: {self.save_file_path}\n')
            self.raw_data = self.load_json(self.save_file_path)
            self.file_stats(self.raw_data)

    def get_asteroid_data_by_id(self, asteroid_id):
        response = requests.get(f'https://api.nasa.gov/neo/rest/v1/neo/{asteroid_id}?api_key={self.api_key}')
        raw_data = response.json()
        time.sleep(3)
        return raw_data["orbital_data"]
    
    def process_data(self):
        processed_data = []
        for asteroid in self.all_neos:
            ast_data = self.get_asteroid_data_by_id(asteroid['id'])
            ast_dict = {
                "id": asteroid['id'],
                "name": asteroid['name'],
                "velocity": asteroid['close_approach_data'][0]['relative_velocity'],
                "miss_distance": asteroid['close_approach_data'][0]['miss_distance'],
                "perihelion_time": ast_data['perihelion_time'],
                "ascending_node_longitude": ast_data['ascending_node_longitude']
            }

            processed_data.append(ast_dict)
            print(f'Asteroid {asteroid["name"]} - {asteroid["id"]} - Complete')


        print(processed_data[0])

    def run_asteroid_data(self):
        self.get_raw_data()
        # self.process_data()

AsteroidData(url="https://api.nasa.gov/neo/rest/v1/feed?api_key=",
             api_key_path="NASA/api_key.json", 
             save_file_path="NASA/meteor/Cache/raw/NEO_raw",
             processed_file_path="NASA/meteor/Cache/processed/NEO_processed"
             ).run_asteroid_data()
