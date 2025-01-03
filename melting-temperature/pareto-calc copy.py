from turtle import title
import pandas as pd
import plotly.express as px
from pymatgen.core import Structure
import plotly.graph_objects as go
from scipy.__config__ import show
from kat.nlc import get_ordering_name, convert_abc_to_hc, get_h_character

# Load the CSV file into a DataFrame
df = pd.read_csv("/home/knykiel/projects/mxene-nlc/melting-temperature/melting-temp-convex-marked.csv")

# Create a column for chemical-system based on formula
df['chemical_system'] = df['structure'].apply(lambda x: Structure.from_dict(eval(x)).composition.chemical_system)

df['hc_ordering'] = df['structure'].apply(lambda struct: convert_abc_to_hc(get_ordering_name(Structure.from_dict(eval(struct)))))

df['h_character'] = df['hc_ordering'].apply(lambda x: get_h_character(x))

# Create a column for the ratio of the two items in the composition dict
df['composition_ratio'] = df['structure'].apply(lambda x: Structure.from_dict(eval(x)).composition.get_el_amt_dict().values()) # type: ignore
df['composition_ratio'] = df['composition_ratio'].apply(lambda x: list(x)[0] / list(x)[1])

df['n'] = df['composition_ratio'].apply(lambda x: 1 if x == 2 else (2 if x == 1.5 else 3))
df['n'] = df['n'].apply(lambda x: int(x))

df["T_m"] = (df["T_ml"] + df["T_mB"] + df["T_mC"]) / 3

fig = go.Figure()
colorscale = px.colors.qualitative.Bold
# color_map = {1:0, 2:3, 3:2}
# Color the markers by energy_above_hull

for i in [1,2,3]:

    df_i = df[df['n'] == i]
    fig.add_trace(
        go.Scatter(
            x=df_i['T_m'],
            y=df_i['energy_above_hull'],
            mode='markers',
            name=f'n={i}',
            marker=dict(
                size=10,
                color=colorscale[i],
                line=dict(width=1),
                symbol=['star' if '*' in formula else 'square' if '^' in formula else 'circle' for formula in df_i['formula']],
            ),
        )
    )

# Add a second empty trace with a star
fig.add_trace(
    go.Scatter(
        x=[None],
        y=[None],
        name='Exp.',
        mode='markers',
        marker=dict(
            size=10,
            color='black',
            symbol='star'
        ),
        showlegend=True
    )
)

# Add a second empty trace with a star
fig.add_trace(
    go.Scatter(
        x=[None],
        y=[None],
        name='MP',
        mode='markers',
        marker=dict(
            size=10,
            color='black',
            symbol='square'
        ),
        showlegend=True
    )
)

# Add a second empty trace with a star
fig.add_trace(
    go.Scatter(
        x=[None],
        y=[None],
        name='This Work',
        mode='markers',
        marker=dict(
            size=10,
            color='black',
            symbol='circle'
        ),
        showlegend=True
    )
)


# Sort the DataFrame by melting temperature in descending order
sorted_df = df.sort_values('T_m', ascending=False)
sorted_df = sorted_df[sorted_df['energy_above_hull'] < 0.2]

# Add annotations for the 5 highest melting temperatures with energy_above_hull below 0.2

fig.update_layout(

    # yaxis_title='Bulk Modulus (GPa)',
    yaxis_title='E<sub>hull</sub> (eV/atom)',
    xaxis_title='Predicted T<sub>M</sub> (K)',
    template="simple_white",
    font=dict(
        family="Helvetica",
        size=14

    ),
    width=800,
    height=400,
    margin=dict(l=20, r=20, t=20, b=20) ,

    xaxis=dict(mirror=True, showgrid=True),
    yaxis=dict(mirror=True, showgrid=True),
    legend=dict(x=1, y=1, xanchor="right", yanchor="top"),
    showlegend=True
    )




# fig.show()
# Show the plot
fig.write_image("ml-convex-pareto-eh-mp.png", scale=3)