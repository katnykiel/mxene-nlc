import pandas as pd
import matgl
import ast
from pymatgen.core import Structure
import plotly.graph_objects as go
import numpy as np
from scipy.optimize import curve_fit

# Load the CSV file
df = pd.read_csv("melting-temp.csv")

# For each row, add a new column that is the average of the T_m predictions
df["T_m_avg"] = df[["T_ml"]].mean(axis=1)

model = matgl.load_model("MEGNet-MP-2018.6.1-Eform")

# For each row, load in the structure and predict the formation energy with matgl
for i, row in df.iterrows():
    structure_str = row["structure"]
    structure_expr = ast.literal_eval(structure_str)
    struct = Structure.from_dict(structure_expr)
    eform = model.predict_structure(struct)
    df.at[i, "E_form"] = float(eform)

# Sort the data by run_time
sorted_data = df.sort_values(by="T_m_avg", ascending=False)

# Initialize the best c_diff value to a large number
best_E_form = float("5")

# Initialize the list of Pareto optimal points
pareto_front = []

# Iterate over the sorted data
for _, row in sorted_data.iterrows():
    # If the current E_form is better than the best found so far
    if row["E_form"] < best_E_form:
        # Update the best E_form
        best_E_form = row["E_form"]
        # Add the current point to the Pareto front
        pareto_front.append(row)

# Convert the Pareto front to a DataFrame
pareto_front = pd.DataFrame(pareto_front)

print(pareto_front)


def exponential(x, a, b, c):
    return a * b**x - c


# Fit a power law to the Pareto front data
popt, _ = curve_fit(exponential, pareto_front["T_m_avg"], pareto_front["E_form"])

# Plot the Pareto curve
fig = go.Figure(
    data=go.Scatter(
        x=df["T_m_avg"],
        y=df["E_form"],
        mode="markers",
        name="T<sub>m</sub> predictions",
    )
)

# Add a trace to the scatter plot that shows the power law fit
x_fit = np.linspace(10, 4500, 100)
y_fit = exponential(x_fit, *popt)
fig.add_trace(
    go.Scatter(
        x=x_fit,
        y=y_fit,
        mode="lines",
        name=f"Pareto front",
    )
)


fig.update_layout(
    xaxis_title="T<sub>m</sub> (K)",
    yaxis_title="E<sub>form</sub> (eV/atom)",
    width=600,
    height=600,
    template="simple_white",
    xaxis=dict(mirror=True, autorange="reversed"),
    yaxis=dict(mirror=True),
    legend=dict(x=0.66, y=0.9),
    font_size=14,
)
fig.write_image("pareto.png", scale=3)
