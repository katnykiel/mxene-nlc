import pandas as pd

# Specify the path to the JSON file
json_file = '/home/knykiel/projects/mxene-nlc/dft-stability/convex-hulls/convex_hull_docs.json'

# Load the JSON data into a DataFrame
data = pd.read_json(json_file)

# for each chemical system, print out the mean energy above hull and the number of systems with energy above hull < 0.1 eV/atom
for chemical_system in data['chemical_system'].unique():
    df = data[data['chemical_system'] == chemical_system]
    mean_energy_above_hull = df['energy_above_hull'].mean()
    num_systems_on_threshold = df[df['energy_above_hull'] == 0].shape[0]
    num_systems_below_threshold = df[df['energy_above_hull'] < 0.1].shape[0]
    print(f'Chemical System: {chemical_system}')
    print(f'Mean Energy Above Hull: {mean_energy_above_hull}')
    print(f'Number of Systems on Threshold: {num_systems_on_threshold}')
    print(f'Number of Systems Below Threshold: {num_systems_below_threshold}')
    print()

# Now you can use the 'data' variable to access the imported data as a DataFrame
# For example, you can print the contents of the DataFrame
pass

