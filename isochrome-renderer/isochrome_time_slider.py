import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.widgets import Slider

# load data
with open('means.json', 'r') as f:
    means_data = json.load(f)
means_matrix = np.array(means_data)

with open('variances.json', 'r') as f:
    variances_data = json.load(f)
variances_matrix = np.array(variances_data)

std_matrix = np.sqrt(variances_matrix)
z_scores = {'1%': -2.33, '25%': -0.674, '50%': 0, '75%': 0.674, '99%': 2.33}
intervals = {percentile: means_matrix + z * std_matrix for percentile, z in z_scores.items()}

btm_left = [42.36020227811244, -71.13409264574024]
top_right = [42.383850169141745, -71.10504224250766]
grid_dim = means_matrix.shape

x = np.linspace(btm_left[1], top_right[1], grid_dim[1])
y = np.linspace(top_right[0], btm_left[0], grid_dim[0])
X, Y = np.meshgrid(x, y)

fig, ax = plt.subplots(figsize=(8, 8))
plt.subplots_adjust(left=0.1, bottom=0.25)
cmap = plt.get_cmap('viridis')
norm = mcolors.Normalize(vmin=0, vmax=100)

# onchange for slider
def update(val=None):
    chosen_time = slider.val
    confidence_levels = np.zeros(means_matrix.shape)
    for percentile, interval_matrix in intervals.items():
        new_confidence_level = float(percentile[:-1])
        mask = (interval_matrix <= chosen_time) & (new_confidence_level > confidence_levels)
        confidence_levels[mask] = new_confidence_level
    ax.clear()
    cf = ax.contourf(X, Y, confidence_levels, levels=[1, 25, 50, 75, 99], cmap=cmap, norm=norm, extend='both')
    
    # remove old colorbar
    global cbar
    if cbar:
        cbar.remove()
    
    cbar = fig.colorbar(cf, ax=ax, label='Confidence Level (%)')
    
    ax.set_title(f'Isochrone Map for {chosen_time} Minutes')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')

# initial setup
cbar = None
axcolor = 'lightgoldenrodyellow'
axtime = plt.axes([0.1, 0.1, 0.65, 0.03], facecolor=axcolor)
slider = Slider(ax=axtime, label='Time', valmin=0, valmax=60, valinit=30, valstep=1)

slider.on_changed(update)
update()

plt.show()