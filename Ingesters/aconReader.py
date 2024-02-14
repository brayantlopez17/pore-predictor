"""
This class reads and parses the pdf files from the Aconity machines
into the common monitoring file csv.
"""

# Built-in
import os
import configparser

# Libs
import pandas as pd
import numpy as np

__author__ = 'Brayant Lopez'
__copyright__ = 'Copyright 2023, Tailored Alloys'
__license__ = 'MIT'
__version__ = '0.1.2'

# Global Variables
config = configparser.ConfigParser()
config.read("config.ini")

FREQUENCY = int(config['Aconity']['frequency'])
OFFSET = int(config['Aconity']['offset'])
LAYER_THICKNESS = round(float(config['Aconity']['layer_thickness']), 3)


def layer_thickness_to_num(filepath:str)->int:
    """
    takes the filename from the pcd file, retrieves the layer height and outputs the layer number
    :return: layer num as int
    """
    layer_thickness = filepath[filepath.rfind("/") + 1:filepath.rfind(".")].replace(".", "_")
    layer_num = int(round(float(layer_thickness), 4)/(LAYER_THICKNESS*100))
    return layer_num


def get_layer_to_string(layer_num:int)->str:
    i = layer_num/10
    if i<1:
        return f'00{layer_num}'
    elif 1<=i<10:
        return f'0{layer_num}'
    else:
        return f'{layer_num}'


class AconityFileReader:
    def __init__(self, filepath:str):
        self.filepath = filepath.replace("\\", "/")
        self._directory = filepath[:self.filepath.rfind("/")]
        self.layer = layer_thickness_to_num(self.filepath)

        self.columns = ['t', 'x', 'y', 'z', 'sensor_0', 'sensor_1', 'sensor_2', 'power', 'laser_status', 'state_1']
        self._df = self._create_df()

        self._fix_df()

    def _create_df(self):

        reader = pd.read_csv(self.filepath, delimiter=' ', skiprows=23, header=3, dtype={
            0: int,
            1: float,
            2: float,
            3: float,
            4: int,
            5: int,
            6: int,
            7: int,
            8: int,
            9: int,
        })
        reader.columns = self.columns
        return reader

    def _fix_df(self):
        for col in self.columns:
            if col != "t":
                self._df[col] = np.roll(self._df[col], shift=OFFSET)
            elif col == "t":
                pass

    def _get_output_file(self):
        """
        Function to create the output file. The method starts by creating the new directory. The output file
        takes the layer number by finding the "_" character in the filepath string.
        Returns the filepath to the output csv and populates the layer number.
        """
        self._create_parsed_dir()
        layer_num = get_layer_to_string(self.layer)
        return f"{self._directory}/data/acon-id_{layer_num}_l1.csv"

    def _create_parsed_dir(self):
        if os.path.exists(f"{self._directory}/data"):
            return
        else:
            os.mkdir(f"{self._directory}/data")

    def to_csv(self, output_file:str=""):
        if output_file == "":
            writing_file = self._get_output_file()
        else:
            writing_file = output_file
        self._df.to_csv(writing_file, index=False)

    def to_h5(self, output_file, layer_num:str):
        layer = f"layer_{layer_num}"
        self._df.to_hdf(output_file, key=layer, format="table", data_columns=True, index=False)



if __name__ == "__main__":
    filepath = r"D:\GTADExP_Data\MonitoringData\UTEP51 PCD\UTEP51 PCD\00_15.pcd"
    obj = AconityFileReader(filepath)
    obj.to_h5("acon_003.h5")