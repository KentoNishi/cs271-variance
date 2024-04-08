import json
import numpy as np
import sys
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.widgets import Slider

# load data
chosen_time = int(sys.argv[1])

with open('means.json', 'r') as f:
    D = np.array(json.load(f))

with open('variances.json', 'r') as f:
    V = np.array(json.load(f))

std_matrix = np.sqrt(V)
z_scores = {'1%': -2.33, '25%': -0.674, '50%': 0, '75%': 0.674, '99%': 2.33}
intervals = {percentile: D + z * std_matrix for percentile, z in z_scores.items()}

btm_left = [42.36020227811244, -71.13409264574024]
top_right = [42.383850169141745, -71.10504224250766]
grid_dim = D.shape

x = np.linspace(btm_left[1], top_right[1], grid_dim[1])
y = np.linspace(top_right[0], btm_left[0], grid_dim[0])
X, Y = np.meshgrid(x, y)

fig, ax = plt.subplots(figsize=(8, 8))

cmap = plt.get_cmap('viridis')
norm = mcolors.Normalize(vmin=0, vmax=100)

def generate_isoerine():
    confidence_levels = np.zeros(D.shape)
    for percentile, interval_matrix in intervals.items():
        new_confidence_level = float(percentile[:-1])
        mask = (interval_matrix <= chosen_time) & (new_confidence_level > confidence_levels)
        confidence_levels[mask] = new_confidence_level
    ax.clear()
    
    cf = ax.contourf(X, Y, confidence_levels, levels=[1, 25, 50, 75, 99], cmap=cmap, norm=norm, extend='both')
    ax.set_xticks([])
    ax.set_yticks([])

generate_isoerine()

plt.savefig('images/isoerine.png', pad_inches=0, bbox_inches='tight')
plt.show()