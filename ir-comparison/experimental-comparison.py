import pandas as pd
import plotly.graph_objects as go
# Load data from the specified paths and rename columns, using 8 spaces as a separator
data1 = pd.read_csv('/scratch/negishi/knykiel/ir-workflows/mxene-ir/1.vasp/IR-Spectrum.dat', header=0, names=['v', 'I'], sep=r'\s{8,}')
data2 = pd.read_csv('/scratch/negishi/knykiel/ir-workflows/mxene-ir/2.vasp/IR-Spectrum.dat', header=0, names=['v', 'I'], sep=r'\s{8,}')
data6 = pd.read_csv('/scratch/negishi/knykiel/ir-workflows/mxene-ir/6.vasp/IR-Spectrum.dat', header=0, names=['v', 'I'], sep=r'\s{8,}')

# Normalize the intensity values to have a maximum of 1
data1['I'] = data1['I'] / data1['I'].max()
data2['I'] = data2['I'] / data2['I'].max()
data6['I'] = data6['I'] / data6['I'].max()

# Define constants k, c, and l
kcl = 10**-2.6

# # Add a column 'T' to each dataset
# data1['T'] = -np.log10(data1['I'])
# data2['T'] = -np.log10(data2['I'])
# data6['T'] = -np.log10(data6['I'])

data1['T'] = 10 ** (-kcl * data1['I']) -.003
data2['T'] = 10 ** (-kcl * data2['I']) -.0018
data6['T'] = 10 ** (-kcl * data6['I']) -.0016



# Read in and plot the experimental data from /home/knykiel/projects/mxene-nlc/ir-comparison/ta4c3.dpt and ta4c3o.dpt and ta4c3o2.dpt where the separator is a single comma
data1_exp = pd.read_csv('/home/knykiel/projects/mxene-nlc/ir-comparison/ta4c3.dpt', header=0, names=['v', 'I'], sep=',')
data2_exp = pd.read_csv('/home/knykiel/projects/mxene-nlc/ir-comparison/ta4c3o.dpt', header=0, names=['v', 'I'], sep=',')
data6_exp = pd.read_csv('/home/knykiel/projects/mxene-nlc/ir-comparison/ta4c3o2.dpt', header=0, names=['v', 'I'], sep=',')
# Create figures for each dataset
fig1 = go.Figure()
fig2 = go.Figure()
fig6 = go.Figure()

# Add traces for each dataset
fig1.add_trace(go.Scatter(x=data1_exp['v'], y=data1_exp['I'], mode='lines', name='Ta<sub>4</sub>C<sub>3</sub> 1000 °C', line=dict(color='rgb(66,66,66)')))
fig1.add_trace(go.Scatter(x=data1['v'], y=data1['T'], mode='lines', name='Ta<sub>4</sub>C<sub>3</sub>', line=dict(color='rgb(99,188,179)')))

fig2.add_trace(go.Scatter(x=data2_exp['v'], y=data2_exp['I'], mode='lines', name='Ta<sub>4</sub>C<sub>3</sub> 600 °C', line=dict(color='rgb(66,66,66)')))
fig2.add_trace(go.Scatter(x=data2['v'], y=data2['T'], mode='lines', name='Ta<sub>4</sub>C<sub>3</sub>O', line=dict(color='rgb(99,188,179)')))

fig6.add_trace(go.Scatter(x=data6_exp['v'], y=data6_exp['I'], mode='lines', name='Ta<sub>4</sub>C<sub>3</sub> 25 °C', line=dict(color='rgb(66,66,66)')))
fig6.add_trace(go.Scatter(x=data6['v'], y=data6['T'], mode='lines', name='Ta<sub>4</sub>C<sub>3</sub>O<sub>2</sub>', line=dict(color='rgb(99,188,179)')))

# Update layout for each figure
for fig in [fig1, fig2, fig6]:
    fig.update_layout(
        template="simple_white",
        font=dict(
            family="Nirmala UI",
            size=14
        ),
        width=300,
        height=300,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(
            mirror=True,
            ticks='inside',
            minor=dict(ticks='inside'),
            range=[420, 900]
        ),
        yaxis=dict(
            mirror=True,
            ticks='inside',
            minor=dict(ticks='inside'),
            showticklabels=False,
            # range=[.99, 1]
        ),
        
        xaxis_title='Wavenumber [cm<sup>-1</sup>]',
        yaxis_title='Transmittance [AU]',
        legend=dict(x=1, y=0.02, xanchor="right", yanchor="bottom"),
        showlegend=True,
    )


# Save the plots
fig1.write_image("experimental-ta4c3.png", scale=3)
fig2.write_image("experimental-ta4c3o.png", scale=3)
fig6.write_image("experimental-ta4c3o2.png", scale=3)
