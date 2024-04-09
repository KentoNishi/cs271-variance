import json
import math
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import RegularGridInterpolator

# Load means and variances data
with open('means.json', 'r') as f:
    means_data = json.load(f)
means_matrix = np.array(means_data)

with open('variances.json', 'r') as f:
    variances_data = json.load(f)
variances_matrix = np.array(variances_data)

# Define geographical boundaries and origin
btm_left = [42.36020227811244, -71.13409264574024]  # [latitude, longitude]
top_right = [42.383850169141745, -71.10504224250766]  # [latitude, longitude]
origin = [42.36340914857679, -71.12589555981565]

latitudes = np.linspace(btm_left[0], top_right[0], 100)
longitudes = np.linspace(btm_left[1], top_right[1], 100)

meanTimeInterpolator = RegularGridInterpolator(
    (latitudes, longitudes),
    means_matrix,
    method='linear',
    bounds_error=False,
    fill_value=None
)

varTimeInterpolator = RegularGridInterpolator(
    (latitudes, longitudes),
    variances_matrix,
    method='linear',
    bounds_error=False,
    fill_value=None
)

# Generate random query points
np.random.seed(42)
queries = np.random.uniform(low=[btm_left[0], btm_left[1]], 
                                 high=[top_right[0], top_right[1]], 
                                 size=(3, 2))

def plot_whisker(center_rad, center_theta):
    whisker_len = 1.5
    new_rad = math.sqrt(center_rad ** 2 + whisker_len ** 2)
    r_theta = math.atan2(whisker_len, center_rad)
    theta1 = center_theta - r_theta
    theta2 = center_theta + r_theta
    # plot
    ax.plot([theta1, theta2], [new_rad, new_rad], color='black', linewidth=1)

def plot_point_polar(ax, point):
    # Calculate polar coordinates from origin
    dx = point[1] - origin[1]
    dy = point[0] - origin[0]
    distance = math.sqrt(dx**2 + dy**2)
    angle = math.atan2(dy, dx)

    # Interpolate mean time and variance
    mean_time = meanTimeInterpolator(point)
    variance = varTimeInterpolator(point)
    std_dev = math.sqrt(variance)

    # Plot the main red line
    ax.plot([angle, angle], [mean_time - std_dev, mean_time + std_dev], color='red', linewidth=2)
    ax.scatter([angle], [mean_time], color='blue', zorder=5)

    ax.text(angle, mean_time, "foo", ha='center', va='center', fontsize=10, color='black')

    # Determine the radial distances for the whiskers   
    quartile_len = 0.67 * std_dev

    plot_whisker(mean_time - quartile_len, angle)
    plot_whisker(mean_time + quartile_len, angle)

# Create polar plot
fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})

# Set custom radial labels
radial_ticks = np.linspace(10, 60, 6)  # Generate radial ticks from 10 to 60 by 10
ax.set_yticks(radial_ticks)
ax.set_yticklabels([f'{int(tick)}min' for tick in radial_ticks])

# Remove degree markings
ax.set_xticklabels([])

# Set the radial limits to include your custom tick marks
ax.set_ylim(0, 60)  # Adjusting this to cover 0 to 60

for query in queries:
    plot_point_polar(ax, query)

plt.show()

