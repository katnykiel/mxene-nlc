"""
determine the stacking sequence of a relaxed structure
"""

from kat.nlc import get_ordering_name, convert_abc_to_hc
import pandas as pd
from pymatgen.core import Structure

# load the set of relaxed structures associated with the convex hull
df_hull = pd.read_json("/home/knykiel/projects/mxene-nlc/dft-stability/convex-hulls/convex_hull_docs.json")

hull_structs = [Structure.from_dict(row["structure"])for row in df_hull["output"]]

orderings = [get_ordering_name(struct) for struct in hull_structs]

hc_orderings = [convert_abc_to_hc(ordering) for ordering in orderings]

# get a list of unique hc_orderings
unique_hc_orderings = list(set(hc_orderings))

# get the h_character of each hc ordering


# if one is the reverse of the other, remove one
# manually redefine the orderings to be consistent with SI

# Initialize an empty list to store the pairs
pairs = []

# Use a set to keep track of strings already paired
paired = set()

# Iterate through the list of strings
for i, string in enumerate(unique_hc_orderings):
    # Check if the reverse of the current string is in the list
    # and ensure it's not the same string
    reversed_string = string[::-1]
    if reversed_string in unique_hc_orderings and string not in paired:
        # Check if the reversed string has not been paired yet
        if reversed_string not in paired:
            # Add the pair to the list
            pairs.append((string, reversed_string))
            # Mark both strings as paired
            paired.add(string)
            paired.add(reversed_string)


pass

