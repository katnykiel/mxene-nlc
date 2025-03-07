import pandas as pd
import plotly.express as px
from pymatgen.core import Structure
import plotly.graph_objects as go
from kat.nlc import get_ordering_name, convert_abc_to_hc, get_h_character
from pymatgen.core.periodic_table import Element

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

# write the hc_ordering, T_m, and chemical_system columns to a csv file called stacking.csv
df[['hc_ordering', 'T_m', 'chemical_system', 'K','G','T_d','Y','energy_above_hull','n']].to_csv("stacking.csv", index=False)

# Filter the DataFrame for systems with E_hull < 0.1
filtered_df = df[df['energy_above_hull'] < 0.1]

# Extract the metal element (not C or N) from the chemical system
filtered_df['metal'] = filtered_df['chemical_system'].apply(lambda x: [el for el in x.split('-') if el not in ['C', 'N']][0])

# Count the number of systems for each metal
metal_counts = filtered_df['metal'].value_counts().reset_index()
metal_counts.columns = ['metal', 'count']

# Include metals with a count of 0
selected_metals = ['Ta', 'Ti', 'Hf', 'Zr', 'Nb', 'Mo', 'V', 'W', 'Sc', 'Cr', 'Mn']
metal_counts = pd.DataFrame(selected_metals, columns=['metal']).merge(metal_counts, on='metal', how='left').fillna(0)

# Get the atomic numbers for the metals
metal_counts['atomic_number'] = metal_counts['metal'].apply(lambda x: Element(x).Z)

# Sort by atomic number
metal_counts = metal_counts.sort_values('atomic_number')
# Create traces for the bar chart
import plotly.colors

# Get the plasma colorscale
plasma_colors = plotly.colors.sequential.Darkmint

# Select the first, middle, and last colors
selected_colors = [plasma_colors[0], plasma_colors[len(plasma_colors) // 2], plasma_colors[-1]]

traces = []
for i, n in enumerate(sorted(df['n'].unique())):
    trace = go.Bar(
        x=metal_counts['metal'],
        y=filtered_df[filtered_df['n'] == n]['metal'].value_counts().reindex(metal_counts['metal'], fill_value=0),
        name=f'M<sub>{n+1}</sub>X<sub>{n if n != 1 else ""}</sub>',
        marker_color=selected_colors[i]
    )
    traces.append(trace)


# Create the layout for the bar chart
layout = go.Layout(
    xaxis=dict(title='Transition Metal'),
    yaxis=dict(title='Number of Stable Systems'),
    # as defined by phonon stability and E_hull < 0.1 eV/atom
    barmode='stack',
    font=dict(family="Nirmala UI")
)

# Create the figure and add the traces
fig = go.Figure(data=traces, layout=layout)

# Add vertical dotted lines between Mn/Zr and Mo/Hf
vertical_lines = [
    {'x': (metal_counts[metal_counts['metal'] == 'Mn'].index[0] + metal_counts[metal_counts['metal'] == 'Zr'].index[0]) / 2+1, 'line': dict(color='black', width=1, dash='dot')},
    {'x': (metal_counts[metal_counts['metal'] == 'Mo'].index[0] + metal_counts[metal_counts['metal'] == 'Hf'].index[0]) / 2+1, 'line': dict(color='black', width=1, dash='dot')}
]

annotations = [
    dict(
        x=1.875,
        y=16,
        text="3<i>d</i>",
        showarrow=False,
        font=dict(size=14, color='gray')
    ),
    dict(
        x=6,
        y=16,
        text="4<i>d</i>",
        showarrow=False,
        font=dict(size=14, color='gray')
    ),
    dict(
        x=9,
        y=16,
        text="5<i>d</i>",
        showarrow=False,
        font=dict(size=14, color='gray')
    )
]

for annotation in annotations:
    fig.add_annotation(annotation)

for line in vertical_lines:
    fig.add_vline(x=line['x'], line=dict(color=line['line']['color'], width=line['line']['width'], dash=line['line']['dash']))

# # Add annotation for E_hull < 0.1 eV/atom
# fig.add_annotation(
#     text="E<sub>hull</sub> < 0.1 eV/atom",
#     xref="paper", yref="paper",
#     x=0.015, y=1.0,
#     showarrow=False,
#     font=dict(size=16),
#     xanchor='left',
#     yanchor='top'
# )

fig.update_layout(
    template="simple_white",
    font=dict(
        family="Nirmala UI",
        size=14
    ),
    width=400,
    height=400,
    margin=dict(l=20, r=20, t=20, b=20),
    xaxis=dict(
        mirror=True,
        range=[-.75, len(metal_counts['metal']) - 0.5],
        ticks='inside',
        minor=dict(ticks='inside')
    ),
    yaxis=dict(
        mirror=True,
        ticks='inside',
        minor=dict(ticks='inside', nticks=2)
    ),
    legend=dict(x=0.01, y=.93, xanchor="left", yanchor="top"),
    showlegend=True,
)



# Show the plot
fig.write_image("hull_chart.png", scale=3)