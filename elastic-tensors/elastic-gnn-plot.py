import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math
from pymatgen.core import Structure

# Load data from elastic-gnn-data.json
df = pd.read_json("elastic-data.json")

# Expand derived_properties column into separate columns
df_x = pd.json_normalize(df["derived_properties"])
df_x["structure"] = df["structure"]

# copy df_x to new df and re-add the ordering column
df_x["ordering"] = df["ordering"]


# Clean up unphysical values
df_x = df_x[abs(df_x["k_vrh"]) <= 1000]
df_x = df_x[abs(df_x["g_vrh"]) <= 1000]

# Get rid of all negative values for k_vrh and g_vrh
df_x = df_x[df_x["k_vrh"] >= 0]
df_x = df_x[df_x["g_vrh"] >= 0]

# Define constants from data
hbar = 1.055 * 10 ** (-34)  # J*s
kb = 1.38 * 10 ** (-23)  # J/K
f = 0.013  # unitless

# Iterate over each row in df_x
for index, row in df_x.iterrows():
    # Get the MatGL energies using the MatGL library
    struct = Structure.from_dict(df_x.at[index, "structure"])
    density = float(struct.density) * 10**3  # g/cm^3 -> kg/m^3
    v = float(struct.volume) * 10 ** (-30)  # Angstrom^3 -> m^3
    m = float(struct.composition.weight) * 1.66 * 10 ** (-27)  # amu -> kg
    a = v ** (1 / 3)

    G = df_x.at[index, "g_vrh"] * 10**9
    K = df_x.at[index, "k_vrh"] * 10**9
    T_d = df_x.at[index, "debye_temperature"]

    # Calculate velocities
    v_s = math.sqrt(G / density)
    v_p = math.sqrt((K + (4 / 3) * G) / density)
    v_m = (3 / ((1 / v_p**3) + 2 * (1 / v_s**3))) ** (1 / 3)

    # Calculate theta quantities
    theta_0 = (hbar * v_m) / (a * kb)
    theta_1 = (hbar**2) / (m * a**2 * kb)
    theta_2 = (a**3 * G) / (kb)
    theta_3 = (a**3 * K) / (kb)

    # Predict melting temperature predictions
    T_mA = 21.8671 * theta_0
    T_mB = 17.553 * theta_0 + 0.001985 * theta_2
    T_mC = 11.9034 * theta_0 + 0.000499 * theta_3  #   + 0.00796 * theta_0**2 / theta_1
    T_ml = kb / (9 * hbar**2) * f**2 * a**2 * m * T_d**2

    # Add new columns for the last 4 values
    df_x.at[index, "T_mA"] = T_mA
    df_x.at[index, "T_mB"] = T_mB
    df_x.at[index, "T_mC"] = T_mC
    df_x.at[index, "T_ml"] = T_ml

import matplotlib.pyplot as plt
import seaborn as sns

# Select the columns to plot
data = df_x[["T_mB", "T_mC", "T_ml", "ordering"]]

# Create the pairplot
sns.pairplot(data)
plt.savefig("melting-temp-pairplot.png")

anasori_data = df_x[["T_mB", "T_mC", "T_ml", "ordering"]]
anasori_data["formula"] = df_x["structure"].apply(
    lambda x: Structure.from_dict(x).formula
)

# save anasori_data to csv
anasori_data.to_csv("melting-temp.csv")

# Plot a histogram of the melting temperature predictions in a 2x2 subplot
fig = make_subplots(rows=2, cols=2)

fig.add_trace(go.Histogram(x=df_x["T_mA"], name="PNN A", nbinsx=10), row=1, col=1)
fig.add_trace(go.Histogram(x=df_x["T_mB"], name="PNN B", nbinsx=10), row=1, col=2)
fig.add_trace(go.Histogram(x=df_x["T_mC"], name="PNN C", nbinsx=10), row=2, col=1)
fig.add_trace(go.Histogram(x=df_x["T_ml"], name="Lindemann", nbinsx=10), row=2, col=2)
fig.update_xaxes(title="T<sub>m</sub> (K)", row=1, col=2)
fig.update_xaxes(title="T<sub>m</sub> (K)", row=1, col=1)
fig.update_xaxes(title="T<sub>m</sub> (K)", row=2, col=1)
fig.update_xaxes(title="T<sub>m</sub> (K)", row=2, col=2)

fig.update_layout(
    height=600,
    width=800,
    title_text="Melting Temperature Predictions",
    template="simple_white",
)

fig.update_xaxes(mirror=True)
fig.update_yaxes(mirror=True)

fig.update_xaxes(range=[0, 5000])
fig.write_image(f"melting-temp.png", scale=3)
