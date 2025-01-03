import pandas as pd
import json
import plotly.graph_objects as go
from pymatgen.core import Structure
import plotly.express as px


# load in convex hull results
df = pd.read_json("/home/knykiel/projects/mxene-nlc/dft-stability/convex-hulls/convex_hull_results.json")

e_list = df["E_above_hull"].tolist()
chemical_systems = [Structure.from_dict(s[0]).composition.chemical_system for s in df["structures"]]

# Sort e_list and chemical_systems in alphabetical order by chemical_system
e_list, chemical_systems = zip(*sorted(zip(e_list, chemical_systems), key=lambda x: x[1]))

colors = px.colors.qualitative.Prism

fig = go.Figure()
for i, energies in enumerate(e_list):
    fig.add_trace(go.Box(y=energies, name=chemical_systems[i],orientation='v', line_color=colors[i % 11]))



fig.update_layout(
    yaxis_title='energy above hull (eV/atom)',
    xaxis_title='chemical system',
    template="simple_white",
    font=dict(
        family="Helvetica",

    ),
    margin=dict(l=20, r=20, t=20, b=20) ,
    showlegend=False,
    xaxis=dict(mirror=True, showgrid=True),
    yaxis=dict(mirror=True, showgrid=True),
    xaxis_tickangle=45,
)

# # Add vertical line at 0
# fig.add_shape(
#     type="line",
#     x0=0,
#     y0=0,
#     x1=0,
#     y1=21,
#     line=dict(
#         color="black",
#         width=3,
#     )
# )
fig.write_image("mxene-nlc-convex-hulls.png", scale=3)
