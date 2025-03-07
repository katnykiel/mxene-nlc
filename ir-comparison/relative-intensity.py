import pandas as pd
import plotly.graph_objects as go
# Load data from the specified paths and rename columns, using 8 spaces as a separator
data1 = pd.read_csv('/scratch/negishi/knykiel/ir-workflows/mxene-ir/1.vasp/IR-Spectrum.dat', header=0, names=['v', 'I'], sep=r'\s{8,}')
data2 = pd.read_csv('/scratch/negishi/knykiel/ir-workflows/mxene-ir/2.vasp/IR-Spectrum.dat', header=0, names=['v', 'I'], sep=r'\s{8,}')
data6 = pd.read_csv('/scratch/negishi/knykiel/ir-workflows/mxene-ir/6.vasp/IR-Spectrum.dat', header=0, names=['v', 'I'], sep=r'\s{8,}')

# Create the figure
fig = go.Figure()

# Add traces for each dataset
fig.add_trace(go.Scatter(x=data1['v'], y=data1['I'], mode='lines', name='Ta<sub>4</sub>C<sub>3</sub>'))
fig.add_trace(go.Scatter(x=data2['v'], y=data2['I'], mode='lines', name='Ta<sub>4</sub>C<sub>3</sub>O'))
fig.add_trace(go.Scatter(x=data6['v'], y=data6['I'], mode='lines', name='Ta<sub>4</sub>C<sub>3</sub>O<sub>2</sub>'))

# Update layout to match the layout from distribution.py
fig.update_layout(
    template="simple_white",
    font=dict(
        family="Nirmala UI",
        size=14
    ),
    width=600,
    height=400,
    margin=dict(l=20, r=20, t=20, b=20),
    xaxis=dict(
        mirror=True,
        # showgrid=True,
        ticks='inside',
        minor=dict(ticks='inside')
    ),
    yaxis=dict(
        mirror=True,
        # showgrid=True,
        ticks='inside',
        minor=dict(ticks='inside')
    ),
    xaxis_title='ν [cm<sup>-1</sup>]',
    yaxis_title='Intensity I(ν) [e<sup>2</sup> amu<sup>-1</sup>]',
    legend=dict(x=1, y=1, xanchor="right", yanchor="top"),
    showlegend=True,
)

# Show the plot
fig.write_image("relative-intensity.png", scale=3)

# Normalize the intensity values to have a maximum of 1
data1['I'] = data1['I'] / data1['I'].max()
data2['I'] = data2['I'] / data2['I'].max()
data6['I'] = data6['I'] / data6['I'].max()

# Create the figure for normalized data
fig_normalized = go.Figure()

# Add traces for each normalized dataset
fig_normalized.add_trace(go.Scatter(x=data1['v'], y=data1['I'], mode='lines', name='Ta<sub>4</sub>C<sub>3</sub> (normalized)'))
fig_normalized.add_trace(go.Scatter(x=data2['v'], y=data2['I'], mode='lines', name='Ta<sub>4</sub>C<sub>3</sub>O (normalized)'))
fig_normalized.add_trace(go.Scatter(x=data6['v'], y=data6['I'], mode='lines', name='Ta<sub>4</sub>C<sub>3</sub>O<sub>2</sub> (normalized)'))

# Update layout to match the layout from distribution.py
fig_normalized.update_layout(
    template="simple_white",
    font=dict(
        family="Nirmala UI",
        size=14
    ),
    width=600,
    height=400,
    margin=dict(l=20, r=20, t=20, b=20),
    xaxis=dict(
        mirror=True,
        ticks='inside',
        minor=dict(ticks='inside')
    ),
    yaxis=dict(
        mirror=True,
        ticks='inside',
        minor=dict(ticks='inside')
    ),
    xaxis_title='Wavenumber [cm<sup>-1</sup>]',
    yaxis_title='Intensity I [AU]',
    legend=dict(x=1, y=1, xanchor="right", yanchor="top"),
    showlegend=True,
)

# Show the normalized plot
fig_normalized.write_image("arbitrary-intensity.png", scale=3)