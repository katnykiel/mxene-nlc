import pandas as pd
import json
import plotly.graph_objs as go
import matgl
from pymatgen.core import Structure

model = matgl.load_model("MEGNet-MP-2018.6.1-Eform")

# read the dft-results.json file and store it in a variable
with open("/home/knykiel/projects/mxene-nlc/dft-results.json", "r") as f:
    dft_results = json.load(f)

# create a pandas dataframe from the dft-results
df_results = pd.DataFrame(dft_results)

# Add a new column that is the lattice parameter
df_results["c_matgl"] = df_results["input_structures"].apply(
    lambda x: x["lattice"]["c"]
)
df_results["a_matgl"] = df_results["input_structures"].apply(
    lambda x: x["lattice"]["a"]
)
df_results["c_dft"] = df_results["structures"].apply(lambda x: x["lattice"]["c"])
df_results["a_dft"] = df_results["structures"].apply(lambda x: x["lattice"]["a"])

# Get the MatGL energies using the MatGL library
df_results["e_matgl"] = df_results["input_structures"].apply(
    lambda x: float((model.predict_structure(Structure.from_dict(x))).numpy())
)

df_results.rename(columns={"formation_energies": "e_dft"}, inplace=True)

for l in ["e"]:
    # create scatter plot of magtl vs dft lattice parameter l
    fig_l = go.Figure()
    fig_l.add_trace(
        go.Scatter(
            x=df_results[f"{l}_dft"],
            y=df_results[f"{l}_matgl"],
            mode="markers",
        )
    )

    # add diagonal line
    fig_l.add_trace(
        go.Scatter(
            x=[min(df_results[f"{l}_dft"]), max(df_results[f"{l}_dft"])],
            y=[min(df_results[f"{l}_matgl"]), max(df_results[f"{l}_matgl"])],
            mode="lines",
            line=go.scatter.Line(color="black", dash="dash"),
        )
    )
    fig_l.update_layout(
        title=f"MatGL vs  DFT: formation energy",
        xaxis_title=f"{l}, DFT (eV)",
        yaxis_title=f"{l}, MatGL (eV)",
        template="simple_white",
        width=600,
        height=600,
        showlegend=False,
    )

    # add the RMSE as an annotation in the bottom right of the figure
    fig_l.add_annotation(
        x=0.95,
        y=0.05,
        xref="paper",
        yref="paper",
        text=f"RMSE: {df_results[f'{l}_matgl'].sub(df_results[f'{l}_dft']).abs().mean():.3f} eV",
        showarrow=False,
        font=dict(size=18),
    )

    # mirrror axes
    fig_l.update_xaxes(mirror=True)
    fig_l.update_yaxes(mirror=True)

    # write figures to file with scale 3
    fig_l.write_image(f"{l}_matgl_vs_{l}_dft.png", scale=3)

    fig_l.show()
