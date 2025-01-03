
from pymatgen.core import Structure
import pandas as pd

# Load data from elastic-data.json
df = pd.read_json("/home/knykiel/projects/mxene-nlc/elastic-tensors/elastic-results.json")

for index, row in df.iterrows():

    formula = row["output"]["formula_pretty"]

    if formula in ["Nb2C", "Ta2N", "Ta2C", "W2C", "V2C", "Sc2C"] and row["output"]["nsites"]==3 and row["output"]["structure"]["lattice"]["a"] < 4.0:

        print(f"found a match at {formula}")

        G = row["output"]["derived_properties"]["g_vrh"] 
        K = row["output"]["derived_properties"]["k_vrh"]
        T_d = row["output"]["derived_properties"]["debye_temperature"]
        Y = row["output"]["derived_properties"]["y_mod"]

        print(f"G: {G:.2f} GPa")
        print(f"K: {K:.2f} GPa")
        print(f"T_d: {T_d:.2f} K")

# read the 