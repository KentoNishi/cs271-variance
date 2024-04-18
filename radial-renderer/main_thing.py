# all the code is on this one
import json
import math
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import RegularGridInterpolator

# read the thing
def read_and_convert(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
        all_points_list = []
    def extract_points(data):
        if isinstance(data, dict):
            for value in data.values():
                extract_points(value)
        elif isinstance(data, list) and isinstance(data[0], list):
            all_points_list.append(data)
    extract_points(data)    
    return all_points_list

all_queries = read_and_convert('points_data.txt')

def plot(queries):

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
    max_rad = 0

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
    # np.random.seed(42)
    # queries = np.random.uniform(low=[btm_left[0], btm_left[1]], 
    #                             high=[top_right[0], top_right[1]], 
    #                             size=(3, 2))

    def plot_center(center_rad, center_theta):
        center_len = 1.2
        new_rad = math.sqrt(center_rad ** 2 + center_len ** 2)
        r_theta = math.atan2(center_len, center_rad)
        theta1 = center_theta - r_theta
        theta2 = center_theta + r_theta
        # plot
        ax.plot([theta1, theta2], [new_rad, new_rad], color='black', linewidth=1)

    # plot whiskers
    def plot_whisker(center_rad, center_theta):
        whisker_len = 1.2
        new_rad = math.sqrt(center_rad ** 2 + whisker_len ** 2)
        r_theta = math.atan2(whisker_len, center_rad)
        theta1 = center_theta - r_theta
        theta2 = center_theta + r_theta
        # plot
        ax.plot([theta1, theta2], [new_rad, new_rad], color='black', linewidth=1)

    def plot_hollow_line(ax, point):
        nonlocal max_rad
        # Calculate polar coordinates from origin
        dx = point[1] - origin[1]
        dy = point[0] - origin[0]
        angle = math.atan2(dy, dx)
        print(angle)

        # Interpolate mean time and variance
        mean_time = meanTimeInterpolator(point)
        variance = varTimeInterpolator(point)
        std_dev = math.sqrt(variance)

        # Main line properties
        main_line_width = 10   # controls box width
        hollow_core_width = main_line_width - 2 # Thinner inner line
        extender_width = 1    # Extender line width
        color_outer = 'black'
        color_inner = 'white' # Color of the background for the hollow effect
        quartile_len = .67 * std_dev
        adj_const = 1

        # mean to quartiles

        ax.plot([angle, angle], [mean_time - quartile_len, mean_time + quartile_len],
                color=color_outer, linewidth=main_line_width)
        ax.plot([angle, angle], [mean_time - quartile_len, mean_time + quartile_len],
                color=color_inner, linewidth=hollow_core_width)
        # add blue dot in center
        # ax.scatter([angle], [mean_time], color='blue', zorder=5, s = 3)
        
        # quartiles to whiskers
        ax.plot([angle, angle], [mean_time - quartile_len - adj_const, mean_time - 2 * std_dev], 
                color = 'black', linewidth=extender_width)
        ax.plot([angle, angle], [mean_time + quartile_len + adj_const, mean_time + 2 * std_dev],
                color = 'black', linewidth=extender_width)
        
        # plot_whisker(mean_time - quartile_len, angle)

        # Draw the outer and inner lines
        # ax.plot([angle, angle], [mean_time - std_dev, mean_time + std_dev], 
        #         color=color_outer, linewidth=main_line_width)
        # ax.plot([angle, angle], [mean_time - std_dev, mean_time + std_dev], 
        #         color=color_inner, linewidth=hollow_core_width)
        
        # Plot the mean point as a blue dot
        # ax.scatter([angle], [mean_time], color='blue', zorder=5, s = 4)
        plot_center(mean_time, angle)

        
        plot_whisker(mean_time - std_dev * 2, angle)
        plot_whisker(mean_time + std_dev * 2, angle)

        max_rad = max(max_rad, mean_time + std_dev * 2)

        # Create polar plot
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})

    # put red dot in middle of plot
    ax.scatter([0], [0], color='red', zorder=5)

    # Set custom radial labels
    
    # max_rad_ceiled = int(np.ceil(max_rad / 10.0)) * 10
    radial_ticks = np.linspace(10, 90, 9)
    # print(max_rad_ceiled)
    # radial_ticks = np.linspace(10, max_rad_ceiled, (max_rad_ceiled // 10) + 1)
    ax.set_yticks(radial_ticks)
    ax.set_yticklabels([f'{int(tick)}' for tick in radial_ticks])

    # Remove degree markings
    ax.set_xticklabels([])

    # Set the radial limits
    ax.set_ylim(0, 90)
    # ax.set_ylim(0, max_rad_ceiled)

    for query in queries:
        plot_hollow_line(ax, query)
    
    max_rad_ceiled = int(np.ceil(max_rad / 10.0)) * 10
    radial_ticks = np.linspace(10, max_rad_ceiled, (max_rad_ceiled // 10) + 1)
    ax.set_ylim(0, max_rad_ceiled)

    plt.show()

for queries in all_queries:
    plot(queries)
    print("---")


