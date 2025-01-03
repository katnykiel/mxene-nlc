import pandas as pd
from pymatgen.core import Structure
import ast

# Load the CSV file
df = pd.read_csv("melting-temp-convex.csv")

# Make a column that averages the predicted values
df["T_m"] = (df["T_ml"] + df["T_mB"] + df["T_mC"]) / 3

# Sort the DataFrame by the 'T_ml' column in descending order
df_sorted = df.sort_values("T_m", ascending=False)
top_candidates = df_sorted.head()
print(top_candidates)

# for each row, load in the structure object and save them all to a folder called best_structs as poscar files
for index, row in top_candidates.iterrows():
    structure_str = row["convex_hull_structure"]
    structure_expr = ast.literal_eval(structure_str)
    struct = Structure.from_dict(structure_expr)
    struct.to(f"best_structs/{index}.vasp", fmt="poscar")

# remove strutures and write to file
top_candidates = top_candidates.drop(columns=["structure", "convex_hull_structure"])
top_candidates.to_csv("top_candidates.csv", index=False)