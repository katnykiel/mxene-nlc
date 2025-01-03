import pandas as pd
import plotly.express as px
from pymatgen.core import Structure
import plotly.graph_objects as go

# Load the CSV file into a DataFrame
df = pd.read_csv("melting-temp-convex.csv")
# Create a column for chemical-system based on formula
df['chemical_system'] = df['structure'].apply(lambda x: Structure.from_dict(eval(x)).composition.chemical_system)

# Create a column for the ratio of the two items in the composition dict
df['composition_ratio'] = df['structure'].apply(lambda x: Structure.from_dict(eval(x)).composition.get_el_amt_dict().values()) # type: ignore
df['composition_ratio'] = df['composition_ratio'].apply(lambda x: list(x)[0] / list(x)[1])

df['n'] = df['composition_ratio'].apply(lambda x: 1 if x == 2 else (2 if x == 1.5 else 3))
df['n'] = df['n'].apply(lambda x: int(x))

df["T_m"] = (df["T_ml"] + df["T_mB"] + df["T_mC"]) / 3

fig = go.Figure()
# Group the DataFrame by 'n'
grouped_df = df.groupby('n')
colorscale = px.colors.qualitative.Bold

# Iterate over each group and add a trace to the figure
for n, sub_df in grouped_df:
    fig.add_trace(
        go.Scatter(
            x=sub_df['T_m'],
            y=sub_df['energy_above_hull'],
            mode='markers',
            name=f'n={n}',
            marker=dict(
                size=10,
                color=colorscale[n], # type: ignore
                line=dict(width=1)
            ),
        )
    )

    # Add marginal histograms on the x and y axes
    fig.update_layout(
        xaxis=dict(
            domain=[0, 0.9],
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            domain=[0, 0.9],
            showgrid=False,
            zeroline=False
        ),
        xaxis2=dict(
            domain=[0.9, 1],
            showgrid=False,
            zeroline=False,
            ticks='',
            showticklabels=False
            
        ),
        yaxis2=dict(
            domain=[0.9, 1],
            showgrid=False,
            zeroline=False,
            ticks='',
            showticklabels=False
        ),
        bargap=0,
        hovermode='closest',
    )
    fig.add_trace(
        go.Violin(
            x=sub_df['T_m'],
            yaxis='y2',
            marker=dict(
                color=colorscale[n]
            ),
            showlegend=False,
            side='positive',
            spanmode='hard',
            points=False,
            y0=0,
            width=0.2  # Change the width to a smaller value
        )
    )

    fig.add_trace(
        go.Violin(
            y=sub_df['energy_above_hull'],
            xaxis='x2',
            marker=dict(
                color=colorscale[n]
            ),
            showlegend=False,
            side='positive',
            spanmode='hard',
            points=False,
            x0=0,
            width=0.2  # Change the width to a smaller value
        )
    )

    # Overlay violin plots on top of each other
    fig.update_layout(violingap=0, violinmode='overlay')

# Create a scatter plot using Plotly
# fig = px.scatter(df, y="energy_above_hull", x="T_ml", hover_data=["formula","ordering"])

# Reverse the x-axis
# fig.update_xaxes(autorange="reversed")
# Sort the DataFrame by melting temperature in descending order
sorted_df = df.sort_values('T_m', ascending=False)
sorted_df = sorted_df[sorted_df['energy_above_hull'] < 0.2]

# Add annotations for the 5 highest melting temperatures with energy_above_hull below 0.2

# for i, row in sorted_df.head(3).iterrows():
#     fig.add_annotation(
#         x=row['T_m'],
#         y=row['energy_above_hull'],
#         text=f"Formula: {row['formula']}",
#         showarrow=True,
#     )

fig.update_layout(
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
    legend=dict(x=.9, y=.9, xanchor="right", yanchor="top"),
    )


fig.show()

# Show the plot
fig.write_image("ml-convex-pareto-n.png", scale=3)