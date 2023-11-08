# Import libraries
import pandas as pd
import numpy as np
from scipy.optimize import curve_fit

# Load the convergence data from the converged_structs.json file with pandas
convergence_data = pd.read_json("converged_structs.json")

# Add a new column that is the lattice parameter
convergence_data["c"] = convergence_data["structures"].apply(
    lambda x: x["lattice"]["c"]
)

# Create a plotly go contour plot of ENCUT and KPOINTS vs. lattice parameter a
import plotly.graph_objects as go

fig = go.Figure(
    data=[
        go.Contour(
            x=convergence_data["ENCUT"],
            y=convergence_data["KPOINTS"],
            z=convergence_data["c"],
            colorbar=dict(title="c (Å)"),
        )
    ]
)


fig.update_layout(
    title="Ta4C3 Convergence Testing",
    xaxis_title="ENCUT (eV))",
    yaxis_title="KPOINTS",
    width=600,
    height=600,
    template="simple_white",
)

# Write the figure to a png file
fig.write_image("convergence.png", scale=3)
# fig.show()

# Generate a new column which is the difference between the calculated c and 28.7237
convergence_data["c_diff"] = abs(convergence_data["c"] - 28.7237)

# Convert the run_time column to minutes
convergence_data["run_time"] = convergence_data["run_time"] / 60

# Create a plotly go scatter plot of run_time vs. c_diff
fig2 = go.Figure(
    data=[
        go.Scatter(
            x=convergence_data["run_time"],
            y=convergence_data["c_diff"],
            mode="markers",
            hovertext=[
                f"ENCUT: {encut}<br>KPOINTS: {kpoints}"
                for encut, kpoints in zip(
                    convergence_data["ENCUT"], convergence_data["KPOINTS"]
                )
            ],
            name="DFT data",
        )
    ]
)

# Sort the data by run_time
sorted_data = convergence_data.sort_values(by="run_time")

# Initialize the best c_diff value to a large number
best_c_diff = float("inf")

# Initialize the list of Pareto optimal points
pareto_front = []

# Iterate over the sorted data
for _, row in sorted_data.iterrows():
    # If the current c_diff is better than the best found so far
    if row["c_diff"] < best_c_diff:
        # Update the best c_diff
        best_c_diff = row["c_diff"]
        # Add the current point to the Pareto front
        pareto_front.append(row)

# Convert the Pareto front to a DataFrame
pareto_front = pd.DataFrame(pareto_front)


def power_law(x, a, b):
    return a * np.power(x, b)


# Fit a power law to the Pareto front data
popt, _ = curve_fit(power_law, pareto_front["run_time"], pareto_front["c_diff"])

# Add a trace to the scatter plot that shows the power law fit
x_fit = np.linspace(0.1, 35, 100)
y_fit = power_law(x_fit, *popt)
fig2.add_trace(
    go.Scatter(
        x=x_fit,
        y=y_fit,
        mode="lines",
        name=f"Pareto front",
    )
)
# Iterate over the sorted data
for _, row in sorted_data.iterrows():
    # Calculate the expected c_diff value for the current run_time value using the power_law function and popt
    expected_c_diff = power_law(row["run_time"], *popt)
    # If the current point is below the best fit line
    if row["c_diff"] < expected_c_diff:
        if row["run_time"] < 10:
            fig2.add_annotation(
                x=row["run_time"],
                y=row["c_diff"],
                text=f"K: {row['KPOINTS']}<br>E: {row['ENCUT']}",
                showarrow=True,
                arrowhead=1,
                ax=0,
                ay=-60,
            )


fig2.update_layout(
    title="Ta4C3 Convergence Testing",
    xaxis_title="Run Time (min)",
    yaxis_title="c error (Å)",
    width=600,
    height=600,
    template="simple_white",
    xaxis=dict(mirror=True),
    yaxis=dict(mirror=True),
    legend=dict(x=0.7, y=0.9),
)
# Write the figure to a png file
fig2.write_image("convergence-pareto.png", scale=3)
# fig2.show()

# use run_time as color
fig3 = go.Figure(
    data=[
        go.Contour(
            x=convergence_data["ENCUT"],
            y=convergence_data["KPOINTS"],
            z=convergence_data["run_time"],
            colorbar=dict(title="run_time (min)"),
        )
    ]
)

fig3.update_layout(
    title="Ta4C3 Convergence Testing",
    xaxis_title="ENCUT (eV))",
    yaxis_title="KPOINTS",
    width=600,
    height=600,
    template="simple_white",
)

# Write the figure to a png file
fig3.write_image("convergence-run_time.png", scale=3)
# fig.show()
