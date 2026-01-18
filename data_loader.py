import json
import pandas as pd

class DataLoader:
    def __init__(self, filepath):
        self.filepath = filepath
        self.data = None

    def load_data(self):
        try:
            with open(self.filepath, 'r', encoding='utf-8') as file:
                raw_data = json.load(file)
            
            self.data = pd.DataFrame(raw_data)
            self.data['timestamp'] = pd.to_datetime(self.data['timestamp'])
            self.data.fillna('', inplace=True)
            
            print(f"Loaded {len(self.data)} records from {self.filepath}")
            return self.data
            
        except Exception as error:
            print(f"Failed to load data: {error}")
            return pd.DataFrame()

    def get_data(self):
        return self.data if self.data is not None else self.load_data()
