import pandas as pd
import numpy as np
import json

class LayerKinematics:
    """
    This class will take a file from the common monitoring file format and
    calculate the time and distance the laser is on and off.
    public methods:
        - get_values()->dict: returns a dictionary with the time and distance values
    """
    def __init__(self, filepath:str):
        self.filepath = filepath
        self.df = pd.read_csv(self.filepath)

        self.df['length'] = np.sqrt(self.df["x"].diff() ** 2 + self.df["y"].diff() ** 2)
        self._events()
        self._polygon_delays()

        self.time_on = float()
        self.time_off = float()
        self.no_events = int()
        self.distance_on = float()
        self.distance_off = float()

        self._calculate_time_distance_on()
        self._calculate_time_distance_off()
        self._retrieve_no_events()

        self.summary = {
            'time on': self.time_on,
            'time off': self.time_off,
            'distance on': self.distance_on,
            'distance off': self.distance_off,
            'total distance': self.distance_on + self.distance_off,
            'total time': self.time_on + self.time_off,
            'number events': self.no_events
        }

    def _calculate_time_distance_on(self):
        df_on = self.df[self.df['laser_status'] == 1]
        self.distance_on = df_on['length'].sum()/1000
        self.time_on = len(df_on)*10/1000000

    def _calculate_time_distance_off(self):
        df_off = self.df[self.df['laser_status'] == 0]
        self.distance_off = df_off['length'].sum()/1000
        self.time_off = len(df_off) * 10 / 1000000

    def _retrieve_no_events(self):
        df = self.df[self.df['event'] == 1]
        self.no_events = len(df) + 1

    def get_values(self):
        return self.summary

    def to_json(self,output_file:str):
        with open(output_file, 'w') as fp:
            json.dump(self.summary, fp)

    def to_csv(self, output_file:str):
        self.df.to_csv(output_file, index=False)

    def _events(self):
        """
        Adds the events columns and curates it
        """
        self.df['event'] = self.df['laser_status'].diff()
        self.df['event'] = self.df['event'].fillna(0)
        self.df['event'] = self.df['event'].astype(int)

    def _polygon_delays(self):
        self.df['polygons'] = np.where(self.df['length'] == 0.0, 1, 0)

