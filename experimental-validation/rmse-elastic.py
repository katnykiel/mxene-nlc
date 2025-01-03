table = [
    ['Nb2C&', '62', '223', '394', '69', '220', '414'],
    ['Ta2N&', '118', '270', '387', '118', '271', '387'],
    ['Ta2C&', '146', '260', '431', '147', '258', '433'],
    ['W2C&', '156', '315', '437', '159', '315', '441'],
    ['V2C&', '100', '219', '623', '102', '219', '630'],
    ['Sc2C&', '9', '71', '223', '13', '73', '265']
]

transposed_table = list(zip(*table))
G = [float(_) for _ in transposed_table[4]]
K = [float(_) for _ in transposed_table[5]]
Td = [float(_) for _ in transposed_table[6]]
G_mp = [float(_) for _ in transposed_table[1]]
K_mp = [float(_) for _ in transposed_table[2]]
Td_mp = [float(_) for _ in transposed_table[3]]

# get the RMSE between each of the properties
from sklearn.metrics import mean_squared_error

G_rmse = mean_squared_error(G, G_mp, squared=False)
K_rmse = mean_squared_error(K, K_mp, squared=False)
Td_rmse = mean_squared_error(Td, Td_mp, squared=False)

print(f"G RMSE: {G_rmse}")
print(f"K RMSE: {K_rmse}")
print(f"TD RMSE: {Td_rmse}")
