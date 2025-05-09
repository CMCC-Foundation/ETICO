import sys
import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset
from scipy.spatial import KDTree
import matplotlib.tri as mtri
import heapq

# Parametri di input
nc_file = sys.argv[1]

# Carica NetCDF
ds = Dataset(nc_file)

lats = ds.variables['latitude'][:]
lons = ds.variables['longitude'][:]
depths = ds.variables['total_depth'][:]
elements = ds.variables['element_index'][:, :] - 1  # from 1-based to 0-based indexing

coords = np.column_stack((lats, lons))
kdtree = KDTree(coords)

# Mappa nodo → nodi adiacenti
node_neighbors = {}
for tri in elements:
    for i in range(3):
        n1, n2 = tri[i], tri[(i + 1) % 3]
        node_neighbors.setdefault(n1, set()).add(n2)
        node_neighbors.setdefault(n2, set()).add(n1)

# Plot con tripcolor
# Crea triangolazione esplicita
triang = mtri.Triangulation(lons, lats, elements)

# Plot tripcolor su batimetria
plt.figure(figsize=(12, 10))
tpc = plt.tripcolor(triang, depths, shading='gouraud', cmap='viridis')
plt.colorbar(tpc, label='Total Depth (m)')

plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.title("Percorso sulla Batimetria")
plt.legend()
plt.grid(True)
plt.show()
