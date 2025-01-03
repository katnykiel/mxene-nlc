from numpy import size
from kat.atomate2.utils import get_convex_hulls, get_convex_hulls_from_df
import pandas as pd
from kat.plotting import get_plot_layout

df = pd.read_json("/home/knykiel/projects/mxene-nlc/elastic-tensors/elastic-relax-docs.json")

figs = get_convex_hulls_from_df(df, write_results=True)
