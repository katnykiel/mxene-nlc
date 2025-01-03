from numpy import size
from kat.atomate2.utils import get_convex_hulls, get_convex_hulls_from_df
import pandas as pd
from kat.plotting import get_plot_layout

o_df = pd.read_json("/home/knykiel/projects/mxene-nlc/elastic-tensors/elastic-relax-docs.json")

for chemsys in ["C-Ta", "C-Nb", "C-Zr", "N-Ti"]:
    # filter just for Ta-C chemical system
    df = o_df[o_df.apply(lambda x: x.output["chemsys"] == chemsys, axis=1)]

    figs = get_convex_hulls_from_df(df, write_results=True)

    figs[0].update_layout(get_plot_layout())


    figs[0].update_layout(yaxis_title="E<sub>hull</sub> (eV/atom)", width = 600, height = 400, margin = dict(l=20, r=20, t=20, b=20), legend = dict(xanchor="right", yanchor="bottom", x=1, y=0, orientation="v"), xaxis = dict(automargin=True), yaxis = dict(automargin=True), font = dict(size=14))

    figs[0].data[1].update(showlegend=False)
    
      
    figs[0].data[2].name = "MP: Stable"
    figs[0].data[3].name = "MP: Unstable"
    figs[0].data[4].name = "This Work"
    figs[0].data = figs[0].data[0:1] + figs[0].data[-1:] + figs[0].data[1:-1]

    figs[0].write_image(f"dft-convex-hull-{chemsys}.png", scale=3)