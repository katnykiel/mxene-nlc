import pandas as pd
from pymatgen.core import Structure
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

# load convex hull data
df_hull = pd.read_json("/home/knykiel/projects/mxene-nlc/dft-stability/convex-hulls/convex_hull_docs.json")

# load melting temperature data
df_melting = pd.read_csv("/home/knykiel/projects/mxene-nlc/melting-temperature/melting-temp.csv")

# Initialize an empty mapping dictionary
structure_map = {}

# get a list of structs in melting and hull
melting_structs = [eval(struct) for struct in df_melting["structure"].tolist()]
hull_structs = [row["structure"] for row in df_hull["output"]]

df_melting["energy_above_hull"] = None
for struct1 in melting_structs:
    for struct2 in hull_structs:
        structure1 = Structure.from_dict(struct1)
        structure2 = Structure.from_dict(struct2)
        sga = SpacegroupAnalyzer(structure1)
        struct1sym = sga.get_primitive_standard_structure()
        sga = SpacegroupAnalyzer(structure2)
        struct2sym = sga.get_primitive_standard_structure()

        if struct1sym == struct2sym:
            struct1_str = str(structure1.as_dict())
    
            # Perform the mapping operations
            structure_map[struct1_str] = struct2

            print('found match with sym')
            # update the row in df_melting with the value of E_above_hull from df_hull
            df_melting.loc[df_melting["structure"] == str(struct1), "energy_above_hull"] = df_hull.loc[df_hull["output"].apply(lambda x: x["structure"]) == struct2, "energy_above_hull"].values[0] # type: ignore

            # add the convex hull structure to the melting df
            df_melting.loc[df_melting["structure"] == str(struct1), "convex_hull_structure"] = str(struct2)

# write df_melting to file
df_melting.to_csv("/home/knykiel/projects/mxene-nlc/melting-temperature/melting-temp-convex.csv", index=False)

# write the mapping to a file
with open("/home/knykiel/projects/mxene-nlc/melting-temperature/structure_map.json", "w") as f:
    f.write(str(structure_map))
