import pandas as pd
from kat.nlc import get_h_character

file_path = '../melting-temperature/stacking.csv'
df = pd.read_csv(file_path)

# print the number of structures with energy_above_hull < 0.1
print(df[df['energy_above_hull'] < 0.1].shape[0])
print(df[df['energy_above_hull'] < 0.05].shape[0])
print(df[df['energy_above_hull'] ==0].shape[0])

print(df[df['energy_above_hull'] ==0])


# group the dataframe by hc_ordering and out the average values of Tm and energy_above_hull for each group

grouped = df.groupby('hc_ordering').agg({'T_m':'mean', 'energy_above_hull':'mean', 'Y':'mean', 'G':'mean', 'K':'mean'}).reset_index()

# do the same, but report the standard deviation instead of average
grouped_std = df.groupby('hc_ordering').agg({'T_m':'std', 'energy_above_hull':'std', 'Y':'std', 'G':'std', 'K':'std'}).reset_index()

# sort by highest predicted Tm
grouped = grouped.sort_values('energy_above_hull', ascending=False)

# also group them by n and report the same
grouped_n = df.groupby('n').agg({'T_m':'mean', 'energy_above_hull':'mean', 'Y':'mean', 'G':'mean', 'K':'mean'}).reset_index()

grouped_n_std = df.groupby('n').agg({'T_m':'std', 'energy_above_hull':'std', 'Y':'std', 'G':'std', 'K':'std'}).reset_index()

print(grouped)

print(grouped_std)

print(grouped_n)

print(grouped_n_std)


import scipy.stats as stats



# Assuming you have three distributions named dist1, dist2, and dist3
# and their respective average and standard deviation values

dist1 = df[df['n'] == 1]['energy_above_hull']
dist2 = df[df['n'] == 2]['energy_above_hull']
dist3 = df[df['n'] == 3]['energy_above_hull']

# Perform ANOVA test
f_value, p_value = stats.f_oneway(dist1, dist2, dist3)

# Print the results
print("F-value", f_value)
print("p-value:", p_value)
 
# get the column h_character
df['h_character'] = df['hc_ordering'].apply(lambda x: get_h_character(x))

# split the data into three groups where h_character is > 0.8, <0.2, and in between, and perform the ANOVA test for each pair of distributions
dist1 = df[df['h_character'] > 0.8]['energy_above_hull']
dist2 = df[df['h_character'] < 0.1]['energy_above_hull']
dist3 = df[(df['h_character'] >= 0.1) & (df['h_character'] <= 0.8)]['energy_above_hull']    

# print the anova value for the three distributions
f_value1, p_value1 = stats.f_oneway(dist1, dist2, dist3)
print("F-value:", f_value1)
print("p-value:", p_value1)

f_value1, p_value1 = stats.f_oneway(dist1, dist2)
f_value2, p_value2 = stats.f_oneway(dist1, dist3)
f_value3, p_value3 = stats.f_oneway(dist2, dist3)

print("F-value (hcp vs fcc):", f_value1)
print("p-value (hcp vs fcc):", p_value1)
print("F-value (hcp vs mixed):", f_value2)
print("p-value (hcp vs mixed):", p_value2)
print("F-value (fcc vs mixed):", f_value3)
print("p-value (fcc vs mixed):", p_value3)

# print all unique values of h_character, in ascending order
print(df['h_character'].unique())

# analyze the same three distributions again for n and h_character but do it for K instead of energy_above_hull

properties = ['T_m', 'energy_above_hull', 'Y', 'G', 'K', 'T_d']

for p in properties:

    print("Property:", p)

    dist1 = df[df['n'] == 1][p]
    dist2 = df[df['n'] == 2][p]
    dist3 = df[df['n'] == 3][p]

    print('')
    # print the mean and standard deviation of the three distributions
    print("Mean (n=1):", dist1.mean())
    print("Mean (n=2):", dist2.mean())
    print("Mean (n=3):", dist3.mean())
    print("Std (n=1):", dist1.std())
    print("Std (n=2):", dist2.std())
    print("Std (n=3):", dist3.std())

    print('')


    f_value, p_value = stats.f_oneway(dist1, dist2, dist3)

    print("F-value:", f_value)
    print("p-value:", p_value)

    print('')

    dist1 = df[df['h_character'] > 0.8][p]
    dist2 = df[df['h_character'] < 0.1][p]
    dist3 = df[(df['h_character'] >= 0.1) & (df['h_character'] <= 0.8)][p]

    print("Mean (hcp):", dist1.mean())
    print("Mean (fcc):", dist2.mean())
    print("Mean (mixed):", dist3.mean())
    print("Std (hcp):", dist1.std())
    print("Std (fcc):", dist2.std())
    print("Std (mixed):", dist3.std())

    print('')
    f_value1, p_value1 = stats.f_oneway(dist1, dist2, dist3)

    print("F-value:", f_value1)
    print("p-value:", p_value1)