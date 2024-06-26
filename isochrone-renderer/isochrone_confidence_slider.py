import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.widgets import Slider
from scipy.stats import norm
import matplotlib.patheffects as path_effects

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
origin = [42.36340914857679, -71.12589555981565]
grid_dim = means_matrix.shape

x = np.linspace(btm_left[1], top_right[1], grid_dim[1])
y = np.linspace(top_right[0], btm_left[0], grid_dim[0])
X, Y = np.meshgrid(x, y)

fig, ax = plt.subplots(figsize=(10, 8))
# plt.subplots_adjust(left=0.1, bottom=0.25)
cmap = plt.get_cmap('viridis')
cnorm = mcolors.Normalize(vmin=means_matrix.min(), vmax=means_matrix.max())
cbar = None

key_mapping = {"A<B": "A-lt-B", "A=B": "A-eq-B", "A>B": "A-gt-B"}

# update based on selected confidence level
def update(val=None, points=None, title=None):
    global cbar
    percentile = 90
    z = norm.ppf(percentile / 100.0)
    interval_matrix = means_matrix + z * std_matrix  # Calculate time range for the selected confidence level
    
    ax.clear()
    cf = ax.contourf(X, Y, interval_matrix, levels=np.linspace(means_matrix.min(), means_matrix.max(), num=100), cmap=cmap, norm=cnorm, extend='both')
    
    if cbar is not None:
        cbar.remove()
    cbar_ticks = np.arange(0, means_matrix.max() + 10, 10)
    cbar = fig.colorbar(cf, ax=ax, label='Time (Minutes)', ticks=cbar_ticks)
    
    if points is not None:
        path_effect = [path_effects.withStroke(linewidth=4, foreground='black')]
        point1 = points[0]
        point2 = points[1]
        p1_scatter = ax.scatter(point1[1], point1[0], color='blue', s=100, edgecolors='white')
        p1_text = ax.text(point1[1] + 0.0012, point1[0], 'A', fontsize=24, color='white', ha='center', va='center', path_effects=path_effect)
        p2_scatter = ax.scatter(point2[1], point2[0], color='blue', s=100, edgecolors='white')
        p2_text = ax.text(point2[1] + 0.0012, point2[0], 'B', fontsize=24, color='white', ha='center', va='center', path_effects=path_effect)
        for artist in [p1_scatter, p1_text, p2_scatter, p2_text]:
            artist.set_clip_on(False)
        
    
    ax.scatter(origin[1], origin[0], color='red', s=100, edgecolors='white')

    # Remove outline on the graph
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    
    # Remove axis labels
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title('')

cbar = None

# slider
# axcolor = 'lightgoldenrodyellow'
# axtime = plt.axes([0.1, 0.1, 0.65, 0.03], facecolor=axcolor)
# slider = Slider(ax=axtime, label='Confidence Level (%)', valmin=1, valmax=99, valinit=50, valstep=1)

# slider.on_changed(update)
# update() 

# plt.show()
                
# load point data
with open('../data-generator/surveyGpsCoordinates.json', 'r') as f:
    point_data = json.load(f)
    for geographic_comparison in point_data:
        for temporal_mean in point_data[geographic_comparison]:
            for temporal_variance in point_data[geographic_comparison][temporal_mean]:
                points = point_data[geographic_comparison][temporal_mean][temporal_variance]
                # round to 2 decimal places
                point_text = f"({points[0][0]:.2f}, {points[0][1]:.2f}), ({points[1][0]:.2f}, {points[1][1]:.2f})"
                title = f"{geographic_comparison}, {temporal_mean}, {temporal_variance} - {point_text}"
                update(None, points, title)
                plt.savefig(f"confidence/{key_mapping[geographic_comparison]} {key_mapping[temporal_mean]} {key_mapping[temporal_variance]}.png")

# plot one with just the origin
ax.clear()
update()
plt.savefig("confidence/origin.png")