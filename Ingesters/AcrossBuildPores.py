"""
The following class uses the porosity data and the laser monitoring
both in the same coordinate system to generate graphs and useful information
about both sets of data.
"""


# Libs
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from tqdm import tqdm

__author__ = 'Brayant Lopez'
__copyright__ = 'Copyright 2023, Tailored Alloys'
__license__ = 'MIT'
__version__ = '0.0.2'

# Global Variables
LAYER_THICKNESS = 0.05              # Layer thickness in mm
LASER_ON = True                     # If True, only the points with laser on will be loaded
LASER_OFF = False                   # If True, only the points with laser off will be loaded


def build_layer_id(i:int):
    """
    Builds the layer id with the format 00i, 0i, i as a string for the common monitoring files name.
    :param i: layer number
    :return: layer id
    """
    j = i//10
    if j < 1:
        return f'00{i}'
    elif 1<=j<10:
        return f'0{i}'
    else:
        return f'{i}'


class MonitoringPorosity:
    """
    Takes the XCT porosity file in the CAD coordinates and the directory with the monitoring files.
    Provides a set of tools to visualize and get an overview of porosity and monitoring.
    Public Methods:
        - load_monitoring_layer()-> df          # Loads the monitoring file for the layer n.
        - get_layer_with_most_pores()-> df      # Returns the layers with the most pores.
        - plot_histogram()-> None               # Plots the histogram of the number of pores per layer.
        - plot_layer_n()-> None                 # Plots the layer n with the pores and the monitoring points.
        - save_image()-> None                   # Saves the image of the layer n with the pores and the monitoring points.
        - get_pores_in_layer_n()-> df           # Returns the pores in the layer n.
        - get_largest_pore()-> df               # Returns the largest pore in the porosity data.
    """

    def __init__(self, xct_porosity_file:str, monitoring_layers_dir:str, xct_pores_2:str):
        self.xct_porosity_file = xct_porosity_file
        self.xct_pores2 = xct_pores_2
        self.monitoring_files_dir = monitoring_layers_dir

        self.porosity_df = self._create_porosity_df()
        self.porosity_per_layer = self._get_porosity_histogram_df()

        self.porosity_df2 = self._create_pores2_df()
        self.porosity2_per_layer = self._get_pore_histogram_df2()

        self.combined_df = self._combine_df()

    def _create_porosity_df(self):
        """
        Creates a dataframe with the porosity data from the xct file. It also adds a layer column and
        checks that the pores are within the range.
        :return: df with the porosity data
        """
        df = pd.read_csv(self.xct_porosity_file)
        df['layer'] = (df['Center z [mm]'].apply(lambda x: int(round(x+18, 3) / LAYER_THICKNESS)))
        #
        df = df[(df['Center x [mm]'] > -25.18) & (df['Center x [mm]'] < 25.18)]
        df = df[(df['Center y [mm]'] > (25.18 - df['Center x [mm]'].abs())*-1) & (df['Center y [mm]'] < (25.18 - df['Center x [mm]'].abs()))]
        return df

    def _create_pores2_df(self):
        """
        Creates a dataframe with the porosity data from the xct file. It also adds a layer column and
        checks that the pores are within the range.
        :return: df with the porosity data
        """
        df = pd.read_csv(self.xct_pores2)
        df['layer'] = (df['Center z [mm]'].apply(lambda x: int(round(x + 18, 3) / LAYER_THICKNESS)))
        #
        df = df[(df['Center x [mm]'] > -25.18) & (df['Center x [mm]'] < 25.18)]
        df = df[(df['Center y [mm]'] > (25.18 - df['Center x [mm]'].abs()) * -1) & (
                    df['Center y [mm]'] < (25.18 - df['Center x [mm]'].abs()))]
        return df

    def _get_porosity_histogram_df(self):
        """
        Creates a dataframe with the number of pores per layer.
        :return: df with the number of pores per layer
        """
        layer_pores = []
        layer = []
        for i in range(1, 848):
            layer_pores.append(len(self.porosity_df[self.porosity_df['layer'] == i]))
            layer.append(i)
        return pd.DataFrame.from_dict({"layer": layer, "pores": layer_pores})

    def _get_pore_histogram_df2(self):
        """
        Creates a dataframe with the number of pores per layer.
        :return: df with the number of pores per layer
        """
        layer_pores = []
        layer = []
        for i in range(1, 848):
            layer_pores.append(len(self.porosity_df2[self.porosity_df2['layer'] == i]))
            layer.append(i)
        return pd.DataFrame.from_dict({"layer": layer, "pores": layer_pores})

    def load_monitoring_layer(self, n:int=1, laser_on=LASER_ON, laser_off = LASER_OFF):
        """
        Loads the monitoring file for the layer n.
        :param n: layer number
        :param laser_on: if True, only the points with laser on will be loaded
        :param laser_off: if True, only the points with laser off will be loaded
        :return: df with the monitoring data
        """
        n = build_layer_id(n)
        filepath = f"{self.monitoring_files_dir}/transformed_id-{n}.csv"
        df = pd.read_csv(filepath)
        if laser_on and not laser_off:
            df = df[df['laser_status'] == 1]
        elif laser_off and not laser_on:
            df = df[df['laser_status'] == 0]

        df = df[(df['power'] > 2700)]                           # ad hoc
        return df.iloc[::10, :]

    def _combine_df(self):
        df = pd.DataFrame()
        layer = self.porosity_per_layer['layer']
        pore_ren = self.porosity_per_layer['pores']
        pores_slm = self.porosity2_per_layer['pores']
        df['layer'], df['Renishaw'], df['SLM'] = layer, pore_ren, pores_slm
        return df


    def plot_histogram(self, name:str,save=False):
        """
        Plots the histogram of the number of pores per layer.
        :param name: name of the plot
        :param save: if True, the plot is saved as an html file
        :return: None
        """
        if name == "Renishaw":
            df = self.porosity_per_layer
        else:
            df = self.porosity2_per_layer
        hist = px.histogram(df, x="layer", y="pores", nbins=len(self.porosity_per_layer))
        hist.update_layout(
            title=f"{name} Pores Distribution",
            xaxis_title="Layer",
            yaxis_title="Pores",
            font=dict(
                family="Courier New, monospace",
                size=18,
                color="RebeccaPurple"
        )
        )
        hist.show()
        if save: hist.to_html(f"{name}_porosity_distribution.html")


    def compare_histograms(self):
        df = self.combined_df
        fig = px.bar(df, x="layer", y=["Renishaw", "SLM"], title="Pore Comparison", barmode='group')
        fig.update_layout(
            xaxis_title="Layers",
            yaxis_title="Pores",
            font=dict(
                family="Courier New, monospace",
                size=18,
                color="RebeccaPurple"
            )
        )
        fig.show()
        fig.write_html("Pore Comparison_bar.html")

    def plot_layer_n(self, n: int, save=False):
        """
        Plots the layer n with the pores and the monitoring points.
        :param n: layer number
        :param save: if True, the plot is saved as an html file
        :return: None
        """
        monitoring_df = self.load_monitoring_layer(n)
        porosity_df = self.porosity_df[self.porosity_df['layer'] == n]
        porosity_df2 = self.porosity_df2[self.porosity_df2['layer'] == n]
        if len(porosity_df) == 0:
            return
        trace_pores = go.Scatter(x=porosity_df['Center x [mm]'], y=porosity_df['Center y [mm]'], mode='markers',
                                 marker=dict(color='red'), name='Renishaw pores')
        trace_monitoring = go.Scatter(x=monitoring_df['x'], y=monitoring_df['y'], mode='markers', opacity=0.3,
                                      hovertext=monitoring_df['power'],
                                      marker=dict(color="gray", colorscale='bluered'), name='monitoring')
        trace_pores2 = go.Scatter(x=porosity_df2['Center x [mm]'], y=porosity_df2['Center y [mm]'], mode='markers',
                                 marker=dict(color='blue'), name='SLM pores')
        # hovertemplate="x: %{x}<br>" +
        #               "y: %{y}<br>" +
        #               f"Power: %{monitoring_df['power']}" +
        #               "<extra></extra>")
        fig = go.Figure(data=[trace_pores, trace_pores2, trace_monitoring])
        fig.update_layout(
            title=f"Layer {n} Pores and Monitoring",
            xaxis_title="x (mm)",
            yaxis_title="y (mm)",
            font=dict(
                family="Courier New, monospace",
                size=18,
                color="RebeccaPurple"
            )
        )
        #fig.show()
        if save: fig.write_html(f"Comparison layer {n} pores.html")



if __name__ == "__main__":
    porosity_filepath = r"C:\Users\Brayant_TA\TailoredAlloys\Test_Data\XCT_Porosity\UTEP-45 Analysis of Porosity correct coords (10262023).csv"
    porosity_filepath2 = r"C:\Users\Brayant_TA\TailoredAlloys\Test_Data\XCT_Porosity\UTEP-49 Analysis of Porosity.csv"
    layers_dir = r"D:\GTADExP_Data\MonitoringData\UTEP 45\UTEP 45\common_monitoring_file"

    obj = MonitoringPorosity(porosity_filepath, layers_dir, porosity_filepath2)

    obj.compare_histograms()
    # for n in range(320, 331):
    #     obj.plot_layer_n(n, save=True)

