import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.widgets import Slider
import matplotlib.patheffects as path_effects
from scipy.stats import norm

# load data
with open('means.json', 'r') as f:
    means_data = json.load(f)
means_matrix = np.array(means_data)

with open('variances.json', 'r') as f:
    variances_data = json.load(f)
variances_matrix = np.array(variances_data)

std_matrix = np.sqrt(variances_matrix)
# z_scores = {'1%': -2.33, '25%': -0.674, '50%': 0, '75%': 0.674, '99%': 2.33}
z_scores = {}
for i in range(1, 100):
    z_scores[f"{i}%"] = norm.ppf(i / 100.0)
intervals = {percentile: means_matrix + z * std_matrix for percentile, z in z_scores.items()}

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
norm = mcolors.Normalize(vmin=0, vmax=100)
cbar = None

key_mapping = {"A<B": "A-lt-B", "A=B": "A-eq-B", "A>B": "A-gt-B"}

# onchange for slider
def update(val=None, points=None, title=None):
    global cbar 
    chosen_time = 45
    confidence_levels = np.zeros(means_matrix.shape)
    for percentile, interval_matrix in intervals.items():
        new_confidence_level = float(percentile[:-1])
        mask = (interval_matrix <= chosen_time) & (new_confidence_level > confidence_levels)
        confidence_levels[mask] = new_confidence_level
    ax.clear()
    cf = ax.contourf(X, Y, confidence_levels, levels=np.arange(0, 101, 1), cmap=cmap, norm=norm, extend='both')
    
    # Handle colorbar creation or update
    if cbar is not None:
        cbar.remove()
    cbar = fig.colorbar(cf, ax=ax, label='Confidence Level (%)')
    cbar.set_ticks(np.arange(0, 101, 10))
    
    # plot points
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
    

# initial setup
# axcolor = 'lightgoldenrodyellow'
# axtime = plt.axes([0.1, 0.1, 0.65, 0.03], facecolor=axcolor)
# slider = Slider(ax=axtime, label='Time', valmin=0, valmax=60, valinit=30, valstep=1)

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
                plt.savefig(f"time/{key_mapping[geographic_comparison]} {key_mapping[temporal_mean]} {key_mapping[temporal_variance]}.png")

# plot one with just the origin
ax.clear()
update()
plt.savefig("time/origin.png")