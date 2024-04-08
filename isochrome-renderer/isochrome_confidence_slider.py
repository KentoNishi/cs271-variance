import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.widgets import Slider
from scipy.stats import norm

# load data
with open('means.json', 'r') as f:
    means_data = json.load(f)
means_matrix = np.array(means_data)

with open('variances.json', 'r') as f:
    variances_data = json.load(f)
variances_matrix = np.array(variances_data)

std_matrix = np.sqrt(variances_matrix)

btm_left = [42.36020227811244, -71.13409264574024]
top_right = [42.383850169141745, -71.10504224250766]
grid_dim = means_matrix.shape

x = np.linspace(btm_left[1], top_right[1], grid_dim[1])
y = np.linspace(top_right[0], btm_left[0], grid_dim[0])
X, Y = np.meshgrid(x, y)

fig, ax = plt.subplots(figsize=(8, 8))
plt.subplots_adjust(left=0.1, bottom=0.25)
cmap = plt.get_cmap('viridis')
cnorm = mcolors.Normalize(vmin=means_matrix.min(), vmax=means_matrix.max())

# update based on selected confidence level
def update(val=None):
    percentile = slider.val
    z = norm.ppf(percentile / 100.0)
    interval_matrix = means_matrix + z * std_matrix  # Calculate time range for the selected confidence level
    
    ax.clear()
    cf = ax.contourf(X, Y, interval_matrix, levels=np.linspace(means_matrix.min(), means_matrix.max(), num=20), cmap=cmap, norm=cnorm, extend='both')
    
    global cbar
    if cbar:
        cbar.remove()
    
    # make the colorbar go in 10 minute increments
    cbar_ticks = np.arange(0, means_matrix.max() + 10, 10)
    cbar = fig.colorbar(cf, ax=ax, label='Time (Minutes)', ticks=cbar_ticks)
    
    ax.set_title(f'Time Range Map at {percentile}% Confidence Level')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')

cbar = None

# slider
axcolor = 'lightgoldenrodyellow'
axtime = plt.axes([0.1, 0.1, 0.65, 0.03], facecolor=axcolor)
slider = Slider(ax=axtime, label='Confidence Level (%)', valmin=1, valmax=99, valinit=50, valstep=1)

slider.on_changed(update)
update() 

plt.show()