import pandas as pd
import plotly.express as px
from pymatgen.core import Structure
import plotly.graph_objects as go
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

# write the hc_ordering, T_m, and chemical_system columns to a csv file called stacking.csv
df[['hc_ordering', 'T_m', 'chemical_system', 'K','G','T_d','Y','energy_above_hull','n']].to_csv("stacking.csv", index=False)


# Filter out rows where '*' or '^' are in the formula
filtered_df = df[~df['formula'].str.contains(r'[\*\^]')]

num_structures = filtered_df[filtered_df['energy_above_hull'] < 0.096].shape[0]
print(f"Number of structures with energy_above_hull < 0.096: {num_structures}")

fig = go.Figure()

viridis_colors = px.colors.sequential.Viridis_r
first_color = viridis_colors[0]
middle_color = viridis_colors[len(viridis_colors) // 2]
last_color = viridis_colors[-1]
colors = [last_color, middle_color, first_color]

# color_map = {1:0, 2:3, 3:2}
# Color the markers by energy_above_hull


def rgb_to_hex(rgb):
    rgb = rgb.strip('rgb()')
    r, g, b = map(int, rgb.split(','))
    return f'#{r:02x}{g:02x}{b:02x}'

viridis_colors_l = px.colors.sample_colorscale(px.colors.sequential.Darkmint, [i/9 for i in range(10)])
viridis_colors_l = [rgb_to_hex(color) for color in viridis_colors_l]

# viridis_colors_l = px.colors.sequential.Viridis_r[0:9]+px.colors.sequential.Viridis_r[-1:]
h_list = [0, 0.16666667, 0.22222222, 0.25, 0.33333333, 0.44444444, 0.5, 0.66666667, 1]
h_list_l = [0.04, 0.15, 0.22, 0.27, 0.34, 0.43, 0.53, 0.71, .92]

h_list_n = sorted(df['h_character'].unique())

# get a list of the midpoints between the values in h_list
h_list_mid = [0] + [(h_list[i] + h_list[i+1]) / 2 for i in range(len(h_list)-1)] + [1]

colorscale = []
for i in range(len(h_list_mid)-1):
    colorscale.append([h_list_mid[i], viridis_colors_l[i]])
    colorscale.append([h_list_mid[i+1], viridis_colors_l[i]])
    fig.add_trace(
        go.Scatter(
            x=df['T_m'],
            y=df['energy_above_hull'],
            mode='markers',
            marker=dict(
                size=8,
                color=df['h_character'],
                colorscale=colorscale,
                colorbar=dict(
                    title='% HCP',
                    tickvals=h_list_l,
                    ticktext=[f'{val*100:.0f}' for val in h_list],
                    tickfont=dict(size=12),
                    yanchor='bottom',  # Set the anchor point of the colorbar to the bottom
                    y=-.1,  # Adjust the y position of the colorbar
                    len=1.1,  # Adjust the length of the colorbar
                ),
                line=dict(width=.6),
                symbol=['star' if '*' in formula else 'square' if '^' in formula else 'circle' for formula in df['formula']],
            ),
            showlegend=False,
            cliponaxis=False  # Allow points to go on top of the axis
        )
    )



# Add a second empty trace with a star
fig.add_trace(
    go.Scatter(
        x=[None],
        y=[None],
        name='Reported (Exp.)',
        mode='markers',
        marker=dict(
            size=8,
            color='black',
            symbol='star',
            line=dict(color='black', width=1)  # Add line color and width
        ),
        showlegend=True
    )
)

# Add a second empty trace with a star
fig.add_trace(
    go.Scatter(
        x=[None],
        y=[None],
        name='Reported (MP)',
        mode='markers',
        marker=dict(
            size=8,
            color='black',
            symbol='square',
            line=dict(color='black', width=1)  # Add line color and width
        ),
        showlegend=True
    )
)

# Add a second empty trace with a star
fig.add_trace(
    go.Scatter(
        x=[None],
        y=[None],
        name='New Materials',
        mode='markers',
        marker=dict(
            size=8,
            color='black',
            symbol='circle',
            line=dict(color='black', width=1)  # Add line color and width

        ),
        showlegend=True
    )
)

# Add marginal histograms on the x and y axes
fig.update_layout(
    xaxis=dict(
        range=[750, 3500],
        domain=[0, 0.9],
        showgrid=False,
        zeroline=False,
        layer='below traces'  # Move x-axis behind the marker points
    ),
    yaxis=dict(
        range=[0, 0.55],
        domain=[0, 1],
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
    bargap=0,
    hovermode='closest',
)

# split up dfs based on h_character using groupby

dfs = []
for h in h_list_n:
    dfs.append(df[df['h_character'] == h])

# df_high = df[df['h_character'] > hcp_cufoff]
# df_low = df[df['h_character'] < fcc_cutoff]
# df_mid = df[(df['h_character'] >= fcc_cutoff) & (df['h_character'] <= hcp_cufoff)]

# dfs = [df_high, df_mid, df_low]

opacity = .9
for n, sub_df in enumerate(dfs):
    h = sub_df['h_character'].iloc[0]
    # fig.add_trace(
    #     go.Violin(
    #         x=sub_df['T_m'],
    #         yaxis='y2',
    #         opacity=opacity,  # Change the opacity to a smaller value
    #         marker=dict(
    #             color=viridis_colors_l[n],
    #         ),
    #         showlegend=False,
    #         side='positive',
    #         spanmode='soft',
    #         points=False,
    #         y0=0,
    #         width=0.2  # Change the width to a smaller value
    #     )
    # )

    fig.add_trace(
        go.Violin(
            y=sub_df['energy_above_hull'],
            xaxis='x2',
            opacity=opacity,  # Change the opacity to a smaller value
            marker=dict(
                color=viridis_colors_l[n],
            ),
            showlegend=False,
            side='positive',
            spanmode='soft',
            points=False,
            x0=0,
            width=0.2,  # Change the width to a smaller value
            fillcolor=f"rgba({int(viridis_colors_l[n][1:3], 16)}, {int(viridis_colors_l[n][3:5], 16)}, {int(viridis_colors_l[n][5:7], 16)}, 0.3)"
        )
    )

# Overlay violin plots on top of each other
fig.update_layout(violingap=0, violinmode='overlay')

# Add a smooth gradient to the figure that starts at y=0 and tapers off by 0.1
for i in range(10):
    fig.add_shape(
        type="rect",
        x0=750,
        y0=i * 0.01,
        x1=3500,
        y1=(i + 1) * 0.01,
        fillcolor=f"rgba(0, 0, 255, {0.3 - i * 0.03})",  # Darker at the bottom
        line=dict(width=0),
        layer="below"
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
        family="Nirmala UI",
        size=14
    ),
    width=800,
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
    legend=dict(x=.9, y=1, xanchor="right", yanchor="top"),
    showlegend=True,
)

# Show the plot
fig.write_image("uhtc-distribution-hc.png", scale=3)