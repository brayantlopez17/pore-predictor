import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots


def read_excel(filepath):
    xls = pd.ExcelFile(filepath)
    df_eos = pd.read_excel(xls, 'eos')
    df_ren = pd.read_excel(xls, 'renishaw')
    df_slm = pd.read_excel(xls, 'slm')
    df_aconity = pd.read_excel(xls, 'aconity')
    return df_eos, df_ren, df_slm, df_aconity

def plot_line(df, attribute):
    if attribute == 'Time On':
        title = 'Time On (s)'
    elif attribute == 'Time Off':
        title = 'Time Off (s)'
    elif attribute == 'Distance On':
        title = 'Travel Distance On (m)'
    elif attribute == 'Travel Distance Off':
        title = 'Distance Off (m)'
    elif attribute == 'avg speed on':
        title = 'Average Speed On (mm/s)'
    elif attribute == 'avg speed off':
        title = 'Average Speed Off (mm/s)'
    elif attribute == 'avg speed':
        title = 'Average Speed (mm/s)'
    else:
        title = attribute
    fig = px.line(df, x="layer", y=attribute, title=title)
    fig.show()


def plot_multiple_df(df_list, attribute):

    df_eos = df_list[0]
    df_ren = df_list[1]
    df_slm = df_list[2]
    df_aco = df_list[3]

    trace_eos = go.Scatter(x=df_eos['Layer'], y=df_eos[attribute], name='EOS', marker=dict(color='blue'))
    trace_ren = go.Scatter(x=df_ren['Layer'], y=df_ren[attribute], name='Renishaw', marker=dict(color='red'))
    trace_slm = go.Scatter(x=df_slm['Layer'], y=df_slm[attribute], name='SLM', marker=dict(color='green'))
    trace_aco = go.Scatter(x=df_aco['Layer'], y=df_aco[attribute], name='Aconity', marker=dict(color='orange'))

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(trace_eos)
    fig.add_trace(trace_ren)
    fig.add_trace(trace_slm)
    fig.add_trace(trace_aco)

    fig.update_layout(height=600, width=1200, title_text=attribute)
    fig.show()
    fig.write_html(f"{attribute}.html")

    # fig = make_subplots(rows=2, cols=2, subplot_titles=("EOS", "Renishaw", "SLM", "Aconity"))
    # fig.add_trace(trace_eos, row=1, col=1)
    # fig.add_trace(trace_ren, row=1, col=2)
    # fig.add_trace(trace_slm, row=2, col=1)
    # fig.add_trace(trace_aco, row=2, col=2)





    # fig = px.line(df, x='Layer', title=attribute)
    # fig.show()

def plot_time_bars(wide_df):
    fig = px.bar(wide_df, x='Layer', y=['time on', 'time off'], title="Aconity Time")
    fig.update_yaxes(title="Time (s)")
    fig.show()
    fig.write_html("Aconity-times.html")


if __name__ == "__main__":
    filepath = "C:/Users/braya/HT_Test/MonitoringData/kinematics_summary.xlsx"
    df_eos, df_ren, df_slm, df_aconity = read_excel(filepath)
    # print(df_eos.columns)
    df_list = [df_eos, df_ren, df_slm, df_aconity]
    attribute = 'distance off'
    plot_multiple_df(df_list, attribute)
    #plot_time_bars(df_aconity)


