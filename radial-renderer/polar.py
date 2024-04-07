"""
still need to figure out labels and whiskers
"""
import json
import math
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import RegularGridInterpolator

with open('means.json', 'r') as f:
    means_data = json.load(f)
means_matrix = np.array(means_data)

with open('variances.json', 'r') as f:
    variances_data = json.load(f)
variances_matrix = np.array(variances_data)

btm_left = [42.36020227811244, -71.13409264574024] # [latitude, longitude]
top_right = [42.383850169141745, -71.10504224250766] # [latitude, longitude]
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

# points to take distance for
np.random.seed(42)
queries = np.random.uniform(low=[btm_left[0], btm_left[1]], 
                                 high=[top_right[0], top_right[1]], 
                                 size=(3, 2))

def plot_whisker(point_x, point_y, perp_angle):
    # plot whisker of length 1 through point at perp_angle
    whisker_len = 1
    x_start = point_x - whisker_len * math.cos(perp_angle)
    y_start = point_y - whisker_len * math.sin(perp_angle)
    x_end = point_x + whisker_len * math.cos(perp_angle)
    y_end = point_y + whisker_len * math.sin(perp_angle)
    plt.plot([x_start, x_end], [y_start, y_end], 'k-')

def plot_point(point):
    # calculate theta from origin
    dx = point[0] - origin[0]
    dy = point[1] - origin[1]
    x_interval = (top_right[0] - btm_left[0]) / 100
    y_interval = (top_right[1] - btm_left[1]) / 100
    matrix_dx = dx / x_interval
    matrix_dy = dy / y_interval
    theta = math.atan2(matrix_dy, matrix_dx)
    # calculate distance from origin via meanTimeInterpolator
    curr_radius = meanTimeInterpolator(point)
    # calculate variance from origin via varTimeInterpolator
    curr_var = varTimeInterpolator(point)
    # plot main line
    full_len = 2 * math.sqrt(curr_var)
    quartile_len = .6745 * math.sqrt(curr_var)
    x_center = curr_radius * math.cos(theta)
    y_center = curr_radius * math.sin(theta)

    full_x_start = x_center - (full_len * math.cos(theta))
    full_y_start = y_center - (full_len * math.sin(theta))
    full_x_end = x_center + (full_len * math.cos(theta))
    full_y_end = y_center + (full_len * math.sin(theta))

    fquartile_x = x_center - (quartile_len * math.cos(theta))
    fquartile_y = y_center - (quartile_len * math.sin(theta))
    tquartile_x = x_center + (quartile_len * math.cos(theta))
    tquartile_y = y_center + (quartile_len * math.sin(theta))

    plot_whisker(fquartile_x, fquartile_y, theta + math.pi / 2)
    plot_whisker(tquartile_x, tquartile_y, theta + math.pi / 2)
    plt.plot([full_x_start, full_x_end], [full_y_start, full_y_end], 'r-')
    plt.scatter(x_center, y_center, color='blue', zorder=5)

    # plot whisker
    perp_theta = theta + math.pi / 2
    perp_theta = perp_theta % (2 * math.pi)
    

for query in queries: 
    plot_point(query)


plt.title('Lines Centered at Points')
plt.grid(True)
plt.axhline(0, color='black', linewidth=0.5)
plt.axvline(0, color='black', linewidth=0.5)
plt.axis('equal')
plt.show()

