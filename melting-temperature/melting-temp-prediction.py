from turtle import title
from matplotlib import legend
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math
import numpy as np
from pymatgen.core import Structure
from torch import dsmm
from kat.nlc import get_ordering_name
import matplotlib.pyplot as plt
import seaborn as sns
from pymatgen.core import Element
import plotly.figure_factory as ff


# Load data from elastic-data.json
df = pd.read_json("/home/knykiel/projects/mxene-nlc/elastic-tensors/elastic-results.json")

# Assume df is your DataFrame and 'matrices' is your column of matrices
def is_positive_definite(matrix):
    try:
        np.linalg.cholesky(matrix)
        return True
    except np.linalg.LinAlgError:
        return False
test_df = df.iloc[0]

# check if output.elastic_tensor is positive definite in df
# df['is_pd'] = df['output'].apply(lambda x: is_positive_definite(x['elastic_tensor']['ieee_format']))

# Filter out the non-positive definite matrices
# df = df[df['is_pd']]
df = df.reset_index(drop=True)

# Define constants from data
hbar = 1.055 * 10 ** (-34)  # J*s
kb = 1.38 * 10 ** (-23)  # J/K
f = 0.10  # unitless

# Iterate over each row in df_x
for index, row in df.iterrows():
    struct = Structure.from_dict(row["output"]["structure"])
    df.at[index,"ordering"] = get_ordering_name(struct)
    density = float(struct.density) * 10**3  # g/cm^3 -> kg/m^3
    v = float(struct.volume) * 10 ** (-30)  # Angstrom^3 -> m^3
    n_atoms = len(struct.sites)
    v /= n_atoms
    m = float(struct.composition.weight) * 1.66 * 10 ** (-27)  # amu -> kg
    m /= n_atoms
    a = v ** (1 / 3)

    G = row["output"]["derived_properties"]["g_vrh"] * 10**9
    K = row["output"]["derived_properties"]["k_vrh"] * 10**9
    T_d = row["output"]["derived_properties"]["debye_temperature"]
    Y = row["output"]["derived_properties"]["y_mod"]

    df.at[index, "rho"] = density
    df.at[index, "G"] = G / 10**9
    df.at[index, "K"] = K / 10**9
    df.at[index, "T_d"] = T_d
    df.at[index, "m"] = m
    df.at[index, "v"] = v
    df.at[index, "Y"] = Y / (10**9)
    df.at[index, "a"] = a

    # Calculate velocities
    v_s = math.sqrt(abs(G / density))
    v_p = math.sqrt(abs((K + (4 / 3) * G) / density))
    v_m = (3 / ((1 / v_p**3) + 2 * (1 / v_s**3))) ** (1 / 3)

    df.at[index, "v_s"] = v_s
    df.at[index, "v_p"] = v_p
    df.at[index, "v_m"] = v_m

    # Calculate theta quantities
    theta_0 = (hbar * v_m) / (a * kb)
    theta_1 = (hbar**2) / (m * a**2 * kb)
    theta_2 = (a**3 * G) / (kb)
    theta_3 = (a**3 * K) / (kb)

    df.at[index, "theta_0"] = theta_0
    df.at[index, "theta_1"] = theta_1
    df.at[index, "theta_2"] = theta_2
    df.at[index, "theta_3"] = theta_3

    # Predict melting temperature predictions
    T_mA = 21.8671 * theta_0
    T_mB = 17.553 * theta_0 + 0.001985 * theta_2
    T_mC = 11.9034 * theta_0 + 0.000499 * theta_3   + 0.00796 * theta_0**2 / theta_1
    # T_ml = kb / (9 * hbar**2) * f**2 * a**2 * m * (T_d)**2
    T_ml = 0
    # # Create lists to store the terms for each T_m
    # terms_mA = []
    # terms_mB = []
    # terms_mC = []
    # terms_ml = []

    # # Iterate over each row in df
    # for index, row in df.iterrows():
    #     # Get the theta values for the current row
    #     theta_0 = row["theta_0"]
    #     theta_1 = row["theta_1"]
    #     theta_2 = row["theta_2"]
    #     theta_3 = row["theta_3"]
        
    #     # Calculate the terms for each T_m and append them to the respective lists
    #     term_mB = [17.553 * theta_0, 0.001985 * theta_2]
    #     term_mC = [11.9034 * theta_0, 0.000499 * theta_3, 0.00796 * theta_0**2 / theta_1]
    #     term_ml = [kb / (9 * hbar**2) * f**2 * a**2 * m * T_d**2]
        
    #     terms_mB.append(term_mB)
    #     terms_mC.append(term_mC)
    #     terms_ml.append(term_ml)

    # # Add new columns for the lists of terms
    # df.at[index, "terms_mB"] = terms_mB
    # df.at[index, "terms_mC"] = terms_mC
    # df.at[index, "terms_ml"] = terms_ml

    # Add new columns for the last 4 values
    df.at[index, "T_mA"] = T_mA
    df.at[index, "T_mB"] = T_mB
    df.at[index, "T_mC"] = T_mC
    df.at[index, "T_ml"] = T_ml

# save G, K, T_d, Y, m, v, a, v_s, v_p, v_m, theta_0, theta_1, theta_2, theta_3, T_mA, T_mB, T_mC, T_ml to csv
input_data_df = df[["G", "K", "T_d", "Y", "m", "v", "a", "v_s", "v_p", "v_m", "theta_0", "theta_1", "theta_2", "theta_3", "T_mA", "T_mB", "T_mC", "T_ml"]]
# Round every value to 5 significant figures
# input_data_df = input_data_df.round(5)
input_data_df.to_csv("melting-temp-input-data.csv")


# Select the columns to plot
data = df[["T_mB", "T_mC", "T_ml"]]
# Select the columns to plot
data = df[["T_mB", "T_mC", "T_ml"]]
data.columns = ["T$_M$, PNN B (K)", "T$_M$, PNN C (K)", "T$_M$, Lindemann (K)"]

# create a seaborn pairplot of the three predictions
sns.pairplot(data)
plt.savefig("melting-temp-pairplot.png", dpi=600)

df["structure"] = df["output"].apply(lambda x: x["structure"])
df["formula"] = df["structure"].apply(lambda x: Structure.from_dict(x).formula)

# Create a column for the ratio of the two items in the composition dict
df['composition_ratio'] = df['structure'].apply(lambda x: Structure.from_dict(x).composition.get_el_amt_dict().values()) # type: ignore
df['composition_ratio'] = df['composition_ratio'].apply(lambda x: list(x)[0] / list(x)[1])

df['n'] = df['composition_ratio'].apply(lambda x: 1 if x == 2 else (2 if x == 1.5 else 3))
df['n'] = df['n'].apply(lambda x: int(x))

anasori_data = df[["T_mB", "T_mC", "T_ml", "ordering", "formula", "structure", "K", "G", "T_d", "Y"]]

# Define a Plotly qualitative color palette
color_palette = px.colors.qualitative.Plotly
 
# save anasori_data to csv
anasori_data.to_csv("melting-temp.csv")

# Scatter plot of each theta value vs. the final melting temperature prediction
theta_values = ["theta_0", "theta_1", "theta_2", "theta_3"]
melting_temps = ["T_mB", "T_mC", "T_ml"]

fig = make_subplots(rows=2, cols=2)


# Add histograms for G, V, T_d, and Y
fig.add_trace(go.Histogram(x=df['G'], name='G', marker_color=color_palette[0]), row=1, col=1)
fig.add_trace(go.Histogram(x=df['K'], name='K', marker_color=color_palette[0]), row=1, col=2)
fig.add_trace(go.Histogram(x=df['T_d'], name='T_d', marker_color=color_palette[0]), row=2, col=1)
fig.add_trace(go.Histogram(x=df['Y'], name='Y', marker_color=color_palette[0]), row=2, col=2)

# Update subplot layout
fig.update_layout(
    template="simple_white",
    font_size=18,
    showlegend=False,
    height = 600,
    width = 1200
)

fig.update_layout(
    margin=dict(l=20, r=20, t=20, b=20)
)

fig.update_xaxes(title_text="G (GPa)", row=1, col=1)
fig.update_xaxes(title_text="K (GPa)", row=1, col=2)
fig.update_xaxes(title_text="T<sub>D</sub> (K)", row=2, col=1)
fig.update_xaxes(title_text="Y (GPa)", row=2, col=2)

fig.update_xaxes(mirror=True)
fig.update_yaxes(mirror=True)

fig.update_xaxes(showgrid=True)
fig.update_yaxes(showgrid=True)

fig.write_image("histograms.png", scale=3)




for temp in melting_temps:
    fig = make_subplots(rows=2, cols=2)
    colormap = px.colors.qualitative.Plotly
    for i, theta in enumerate(theta_values):
        # split up each by n and plot separately
        for n_value in df['n'].unique():
            df_n = df[df['n'] == n_value]
            fig.add_trace(go.Scatter(x=df_n[theta], y=df_n[temp], mode='markers',marker=dict(color=colormap[n_value]), showlegend = (i==0), name=f"n={n_value}", hovertext=df_n['formula']), row=(i//2)+1, col=(i%2)+1)
            fig.update_xaxes(title_text=theta, row=(i//2)+1, col=(i%2)+1)
            fig.update_yaxes(title_text=temp, row=(i//2)+1, col=(i%2)+1)

    fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=600, width=800)
    fig.write_image(f"theta_{temp}_comparison.png", scale=3)
    # fig.show()

# add a column that is the period of the first element in the compositioni dict
df['period'] = df['structure'].apply(lambda x: Structure.from_dict(x).composition.get_el_amt_dict().keys()) # type: ignore
df['period'] = df['period'].apply(lambda x: Element(list(x)[0]).row)

for temp in melting_temps:
    fig = make_subplots(rows=2, cols=2)
    colormap = px.colors.qualitative.Plotly
    for i, theta in enumerate(theta_values):
        # split up each by n and plot separately
        for n_value in df['period'].unique():
            df_n = df[df['period'] == n_value]
            fig.add_trace(go.Scatter(x=df_n[theta], y=df_n[temp], mode='markers',marker=dict(color=colormap[n_value]), showlegend = (i==0), name=f"{n_value}", hovertext=df_n['formula']), row=(i//2)+1, col=(i%2)+1)
            fig.update_xaxes(title_text=theta, row=(i//2)+1, col=(i%2)+1)
            fig.update_yaxes(title_text=temp, row=(i//2)+1, col=(i%2)+1)

    fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=600, width=800, legend=dict(title='Period'))
    fig.write_image(f"theta_{temp}_comparison_period.png", scale=3)
    # fig.show()

for temp in melting_temps:
    fig = make_subplots(rows=2, cols=2)
    colormap = px.colors.qualitative.Plotly
    for i, theta in enumerate(theta_values):
        # split up each by n and plot separately
        for n_value in df['n'].unique():
            df_n = df[df['n'] == n_value]
            fig.add_trace(go.Scatter(x=df_n[theta], y=df_n[temp], mode='markers',marker=dict(color=colormap[n_value]), showlegend = (i==0), name=f"n={n_value}", hovertext=df_n['formula']), row=(i//2)+1, col=(i%2)+1)
            fig.update_xaxes(title_text=theta, row=(i//2)+1, col=(i%2)+1)
            fig.update_yaxes(title_text=temp, row=(i//2)+1, col=(i%2)+1)

    fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=600, width=800, legend=dict(title='M<sub>n+1</sub>X<sub>n</sub>'))
    fig.write_image(f"theta_{temp}_comparison.png", scale=3)
    # fig.show()

# repeat for histograms
fig = make_subplots(rows=2, cols=2)
colormap = px.colors.qualitative.Plotly
for i, theta in enumerate(theta_values):
    # split up each by n and plot separately
    for n_value in df['period'].unique():
        df_n = df[df['period'] == n_value]
        # fig.add_trace(go.Histogram(x=df_n[theta], name=f"{n_value}", marker_color=colormap[n_value],showlegend = (i==0)), row=(i//2)+1, col=(i%2)+1)
        # Plot the histogram as a distribution with area under the curve
        hist, edges = np.histogram(df_n[theta], bins='auto', density=True)
        x = np.linspace(edges[0], edges[-1], 1000)
        y = np.interp(x, edges[:-1], hist)
        fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name=f"{n_value}", line=dict(color=colormap[n_value]), showlegend=(i==0)), row=(i//2)+1, col=(i%2)+1)
        fig.update_xaxes(title_text=theta, row=(i//2)+1, col=(i%2)+1)
        fig.update_yaxes(row=(i//2)+1, col=(i%2)+1)

fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=600, width=800, legend=dict(title='Period'))
fig.write_image(f"theta_histograms_period.png", scale=3)
    # fig.show()

fig = make_subplots(rows=2, cols=2)
colormap = px.colors.qualitative.Plotly
for i, theta in enumerate(theta_values):
    # split up each by n and plot separately
    for n_value in df['n'].unique():
        df_n = df[df['n'] == n_value]
        hist, edges = np.histogram(df_n[theta], bins='auto', density=True)
        x = np.linspace(edges[0], edges[-1], 1000)
        y = np.interp(x, edges[:-1], hist)
        fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name=f"{n_value}", line=dict(color=colormap[n_value]), showlegend=(i==0)), row=(i//2)+1, col=(i%2)+1)
        fig.update_xaxes(title_text=theta, row=(i//2)+1, col=(i%2)+1)
        fig.update_yaxes(row=(i//2)+1, col=(i%2)+1)

fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=600, width=800, legend=dict(title='M<sub>n+1</sub>X<sub>n</sub>'))
fig.write_image(f"theta_histograms.png", scale=3)
    # fig.show()
    

df["n"] = df["n"].apply(lambda x: str(x))

# try with sns
data = df[["T_mB", "T_mC", "T_ml", "period"]]
data.columns = ["T$_M$, PNN B (K)", "T$_M$, PNN C (K)", "T$_M$, Lindemann (K)", "period"]
# create a seaborn pairplot of the three predictions
sns.pairplot(data, hue="period", corner=True, palette="viridis")

plt.savefig("melting-temp-pairplot.png", dpi=600)

df["period"] = df["period"].apply(lambda x: str(x))
# generate a pairplot of the three prediction methods using plotly, and color by n
# fig = px.scatter_matrix(df, dimensions=["T_mB", "T_mC", "T_ml"], color="n", color_discrete_sequence=px.colors.qualitative.Plotly )
fig = px.scatter_matrix(df, dimensions=["T_mB", "T_mC", "T_ml"], color="n", color_continuous_scale=px.colors.qualitative.Plotly)
# fig.update_traces(diagonal_visible=False, showupperhalf=False)
fig.update_layout(width=800, height=800, legend=dict(title="n (M<sub>n+1</sub>X<sub>n</sub>)"))
fig.write_image("melting-temp-pairplot-n.png", scale=3)




fig = make_subplots(rows=2, cols=2)
# Add histograms for a, m, ma**2, and 1/(m*a**2) colored by period
for period in df['period'].unique():
    fig.add_trace(go.Histogram(x=df[df['period'] == period]['a'], name=f'a (Period {period})'), row=1, col=1)
    fig.add_trace(go.Histogram(x=df[df['period'] == period]['m'], name=f'm (Period {period})'), row=1, col=2)
    fig.add_trace(go.Histogram(x=df[df['period'] == period]['a']**2 * df[df['period'] == period]['m'], name=f'ma**2 (Period {period})'), row=2, col=1)
    fig.add_trace(go.Histogram(x=1 / (df[df['period'] == period]['m'] * df[df['period'] == period]['a']**2), name=f'1/(m*a**2) (Period {period})'), row=2, col=2)

# Add x-axis labels
fig.update_xaxes(title_text="a", row=1, col=1)
fig.update_xaxes(title_text="m", row=1, col=2)
fig.update_xaxes(title_text="m*a^2", row=2, col=1)
fig.update_xaxes(title_text="1/(m*a^2)", row=2, col=2)

fig.update_layout(
    template="simple_white",
    # showlegend=False,
    height=600,
    width=800
)
fig.update_layout(
    margin=dict(l=20, r=20, t=20, b=20)
)
fig.write_image("histograms-theta1.png", scale=3)
fig.show()
# try with figure factory
fig = ff.create_scatterplotmatrix(data, diag='histogram', index='period',
                                  height=800, width=800)
# fig.show()



# try with px
fig = px.scatter_matrix(df, dimensions=["T_mB", "T_mC", "T_ml"], color="period", color_continuous_scale=px.colors.qualitative.Plotly)
fig.update_traces(diagonal_visible=False)#, showupperhalf=False)

# Create histograms for T_mB, T_mC, and T_ml
fig.add_trace(go.Histogram(x=df['T_mB'], name='T_mB', marker_color=color_palette[0]), row=1, col=1)
fig.add_trace(go.Histogram(x=df['T_mC'], name='T_mC', marker_color=color_palette[1]), row=2, col=2)
fig.add_trace(go.Histogram(x=df['T_ml'], name='T_ml', marker_color=color_palette[2]), row=3, col=3)

fig.update_layout(width=800, height=800, legend=dict(title="period"))
fig.write_image("melting-temp-pairplot-period.png", scale=3)
# fig.show()

# try with splom
periods = df['period'].astype('category').cat.codes
fig = go.Figure(data=go.Splom(
    dimensions=[
        dict(label="T_mB", values=df['T_mB']),
        dict(label="T_mC", values=df['T_mC']),
        dict(label="T_ml", values=df['T_ml'])
    ],
    # diagonal_visible=False,
    # showupperhalf=False,
    marker=dict(color=periods, showscale=False)
))

fig.update_layout(width=800, height=800 )
fig.write_image("melting-temp-pairplot-period.png", scale=3)
# fig.show()


# Scatter plot of each property vs. the final melting temperature prediction
properties = ["rho", "K", "G", "T_d"]

for temp in melting_temps:
    fig = make_subplots(rows=2, cols=2)

    for i, prop in enumerate(properties):
        fig.add_trace(go.Scatter(x=df[prop], y=df[temp], mode='markers', name=f'{prop} vs. {temp}'), row=(i//2)+1, col=(i%2)+1)
        fig.update_xaxes(title_text=prop, row=(i//2)+1, col=(i%2)+1)
        fig.update_yaxes(title_text=temp, row=(i//2)+1, col=(i%2)+1)

    fig.update_layout(height=600, width=800, title_text=f"Derived Properties vs. {temp}")
    fig.write_image(f"property_{temp}_comparison.png", scale=3)

    # for the highest n values of T_mC, make a spider plot of the derived properties
    # Sort the dataframe by T_mC in descending order
    df_sorted = df.sort_values(temp, ascending=False)

    # Select the top n rows
    n = 16  # Replace with your desired value of n
    top_n = df_sorted.head(n)

    # Create a 4x4 figure with subplots
    fig = make_subplots(rows=4, cols=4, specs=[[{'type': 'polar'} for _ in range(4)] for _ in range(4)])

    # Iterate over each row in top_n
    for i, (index, row) in enumerate(top_n.iterrows()):
        spider_properties = ["rho", "K", "G", "T_d", "m","v"]
        spider_properties = theta_values
        values = [row[prop] / df_sorted[prop].max() for prop in spider_properties]

        # Add scatterpolar subplot
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=spider_properties,
            fill='toself'
        ), row=(i // 4) + 1, col=(i % 4) + 1)

        # Update subplot layout
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=False,
                    range=[0, 1]  # Adjust the range to be between 0 and 1
                )
            ),
            polar2=dict(
                radialaxis=dict(
                    visible=False,
                    range=[0, 1]  # Adjust the range to be between 0 and 1
                )
            ),
            polar3=dict(
                radialaxis=dict(
                    visible=False,
                    range=[0, 1]  # Adjust the range to be between 0 and 1
                )
            ),
            polar4=dict(
                radialaxis=dict(
                    visible=False,
                    range=[0, 1]  # Adjust the range to be between 0 and 1
                )
            ),
            polar5=dict(
                radialaxis=dict(
                    visible=False,
                    range=[0, 1]  # Adjust the range to be between 0 and 1
                )
            ),
            polar6=dict(
                radialaxis=dict(
                    visible=False,
                    range=[0, 1]  # Adjust the range to be between 0 and 1
                )
            ),
            polar7=dict(
                radialaxis=dict(
                    visible=False,
                    range=[0, 1]  # Adjust the range to be between 0 and 1
                )
            ),
            polar8=dict(
                radialaxis=dict(
                    visible=False,
                    range=[0, 1]  # Adjust the range to be between 0 and 1
                )
            ),
            polar9=dict(
                radialaxis=dict(
                    visible=False,
                    range=[0, 1]  # Adjust the range to be between 0 and 1
                )
            ),
            polar10=dict(
                radialaxis=dict(
                    visible=False,
                    range=[0, 1]  # Adjust the range to be between 0 and 1
                )
            ),
            polar11=dict(
                radialaxis=dict(
                    visible=False,
                    range=[0, 1]  # Adjust the range to be between 0 and 1
                )
            ),
            polar12=dict(
                radialaxis=dict(
                    visible=False,
                    range=[0, 1]  # Adjust the range to be between 0 and 1
                )
            ),
            polar13=dict(
                radialaxis=dict(
                    visible=False,
                    range=[0, 1]  # Adjust the range to be between 0 and 1
                )
            ),
            polar14=dict(
                radialaxis=dict(
                    visible=False,
                    range=[0, 1]  # Adjust the range to be between 0 and 1
                )
            ),
            polar15=dict(
                radialaxis=dict(
                    visible=False,
                    range=[0, 1]  # Adjust the range to be between 0 and 1
                )
            ),
            polar16=dict(
                radialaxis=dict(
                    visible=False,
                    range=[0, 1]  # Adjust the range to be between 0 and 1
                )
            ),
            showlegend=False,
        )

    # Update overall figure layout
    fig.update_layout(
        height=800,
        width=800,
        title_text=f"Derived Property Comparison for Top 16 {temp} Values"
    )

    # Save the figure
    fig.write_image(f"top_16_scatterpolars_{temp}.png", scale=3)

    # Calculate the average melting temperature predictions
    avg_T_m = df[["T_mB", "T_mC", "T_ml"]].mean(axis=1)

    # Create the histogram
    fig = go.Figure(data=[go.Histogram(x=avg_T_m, marker_color=color_palette[0])])

    # Update subplot layout
    fig.update_layout(
        template="simple_white",
        font_size=18,
        showlegend=False,
        height=700,
        width=700
    )

    fig.update_xaxes(mirror=True)
    fig.update_yaxes(mirror=True)

    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20)
    )
    
    fig.update_xaxes(showgrid=True)
    fig.update_yaxes(showgrid=True)
    fig.update_xaxes(title_text="Average Melting Temperature (K)")
    fig.update_yaxes(title_text="Count")
    fig.write_image("average-melting-temp-histogram.png", scale=3)

    # Show the histogram
    # fig.show()