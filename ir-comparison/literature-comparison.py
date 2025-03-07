import pandas as pd
import plotly.graph_objects as go
# Load data from the specified paths and rename columns, using 8 spaces as a separator
nb = pd.read_csv('/scratch/negishi/knykiel/ir-workflows/mxene-ir/0.vasp/IR-PeakTable.dat', header=0, names=['v', 'I'], sep=r'\s{4,}')
v = pd.read_csv('/scratch/negishi/knykiel/ir-workflows/mxene-ir/5.vasp/IR-PeakTable.dat', header=0, names=['v', 'I'], sep=r'\s{4,}')
ta = pd.read_csv('/scratch/negishi/knykiel/ir-workflows/mxene-ir/4.vasp/IR-PeakTable.dat', header=0, names=['v', 'I'], sep=r'\s{4,}')

# Normalize the intensity values to the largest positive value for positive v
v['I'] = v.loc[v['v'] > 0, 'I'] / v.loc[v['v'] > 0, 'I'].max()
nb['I'] = nb.loc[nb['v'] > 0, 'I'] / nb.loc[nb['v'] > 0, 'I'].max()
ta['I'] = ta.loc[ta['v'] > 0, 'I'] / ta.loc[ta['v'] > 0, 'I'].max()

# Create dataframes for calculated data
nb_exp = pd.DataFrame({'v': [704, 654, 576, 548, 506, 337, 218, 150], 'I': [1, 1, 1, 1, 1, 1, 1, 1]})
v_exp = pd.DataFrame({'v': [670, 643, 585, 564, 528, 327, 219, 72], 'I': [1, 1, 1, 1, 1, 1, 1, 1]})
ta_exp = pd.DataFrame({'v': [735, 681, 586, 554, 531, 347, 171, 116], 'I': [1, 1, 1, 1, 1, 1, 1, 1]})

# Create figures for each dataset
fig1 = go.Figure()
fig2 = go.Figure()
fig6 = go.Figure()

# Add traces for each dataset as extremely thin bar charts
fig1.add_trace(go.Bar(x=nb_exp['v'], y=nb_exp['I'], width=10, name='Nb (lit.)'))
fig1.add_trace(go.Bar(x=nb['v'], y=nb['I'], width=10, name='Nb'))

fig2.add_trace(go.Bar(x=v_exp['v'], y=v_exp['I'], width=10, name='V (lit.)'))
fig2.add_trace(go.Bar(x=v['v'], y=v['I'], width=10, name='V'))

fig6.add_trace(go.Bar(x=ta_exp['v'], y=ta_exp['I'], width=10, name='Ta (lit.)'))
fig6.add_trace(go.Bar(x=ta['v'], y=ta['I'], width=10, name='Ta'))

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
            range=[420, 1200]
        ),
        yaxis=dict(
            mirror=True,
            ticks='inside',
            minor=dict(ticks='inside'),
            showticklabels=False
        ),
        xaxis_title='Wavenumber [cm<sup>-1</sup>]',
        yaxis_title='Intensity [AU]',
        legend=dict(x=1, y=0.02, xanchor="right", yanchor="bottom"),
        showlegend=True,
    )


# Save the plots
fig1.write_image("literature-nb.png", scale=3)
fig2.write_image("literature-v.png", scale=3)
fig6.write_image("literature-ta.png", scale=3)
