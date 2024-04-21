# %%
# read in ./meanTimeGrid.json, a 99x99 grid of floats
# and visualize it with matplotlib

import json
import numpy as np
import matplotlib.pyplot as plt
import random
from pathlib import Path
import matplotlib.patheffects as pe
import PIL as pil


# read in the json file
with open('meanTimeGrid.json', 'r') as f:
    meanTimeGrid = json.load(f)

# convert the json object to a numpy array
meanTimeGrid = np.array(meanTimeGrid)

mapGrid = pil.Image.open('map.png')
def shift(x):
    return x * 1024 / 100

# plot the grid
plt.imshow(meanTimeGrid, cmap='plasma', interpolation='bilinear')
plt.colorbar()
plt.title('Mean Time Grid')
plt.show()


# %%
# do the same thing with the variance
with open('varianceTimeGrid.json', 'r') as f:
    varianceTimeGrid = json.load(f)

varianceTimeGrid = np.sqrt(np.array(varianceTimeGrid))

plt.imshow(varianceTimeGrid, cmap='viridis', interpolation='bilinear')
plt.colorbar()
plt.title('sqrt(Variance) Time Grid')
plt.show()

# info = {
#     "origin": origin,
#     "originMean": originMean,
#     "originVariance": originVariance,
#     "originX": origin_x,
#     "originY": origin_y,
#     "categoriesIndexOrder": ["distance", "mean", "variance"],
#     
# }
# json.dump({
#     "info": info,
#     "categories": categorized,
# }, open('categorizedGpsCoordinates.json', 'w'))


# put red dot at origin and blue dots at categories["A=B"]["A=B"]["A=B"]

# %%
# read in the categorized gps coordinates
with open('categorizedGpsCoordinates.json', 'r') as f:
    categorized = json.load(f)

with open('surveyGpsCoordinates.json', 'r') as f:
    survey = json.load(f)

# get the origin
origin = categorized['info']['originX'], categorized['info']['originY']
keys = ["A=B", "A<B", "A>B"]
btm_left = [42.36020227811244, -71.13409264574024]
top_right = [42.383850169141745, -71.10504224250766]

for key1 in keys:
    for key2 in keys:
        for key3 in keys:
            try:
                sampled_items = [survey[key1][key2][key3]] # [:4]
            except KeyError:
                continue
            plt.cla()
            fig, axs = plt.subplots(1, 1) # plt.subplots(2, 2)
            for ((((i_1, j_1)), ((i_2, j_2))), ax) in zip(sampled_items, [axs]):
                # plt.cla()
                # plt.imshow(varianceTimeGrid, cmap='viridis', interpolation='bilinear')
                # plt.scatter(origin[1], origin[0], c='r', edgecolors='white')
                # plt.scatter(j_1, i_1, c='b', edgecolors='white')
                # plt.scatter(j_2, i_2, c='b', edgecolors='white')
                # plt.show()
                i_1 = 99 - int((i_1 - btm_left[0]) / (top_right[0] - btm_left[0]) * 99)
                j_1 = int((j_1 - btm_left[1]) / (top_right[1] - btm_left[1]) * 99)
                i_2 = 99 - int((i_2 - btm_left[0]) / (top_right[0] - btm_left[0]) * 99)
                j_2 = int((j_2 - btm_left[1]) / (top_right[1] - btm_left[1]) * 99)
                path_effects = [pe.withStroke(linewidth=4, foreground="black")]
                ax.axis('off')
                ax.imshow(mapGrid, cmap='plasma', interpolation='bilinear')
                ax.margins(x=100, y=100)
                ax.scatter(shift(origin[1]), shift(origin[0]), c='r', edgecolors='white', s=100)
                scatter = ax.scatter(shift(j_1), shift(i_1), facecolor='b', edgecolors='white', s=100)
                scatter.set_clip_on(False)
                ax.text(shift(j_1 + 2.5), shift(i_1 + 3), 'A', fontsize=24, color='white', path_effects=path_effects)
                scatter = ax.scatter(shift(j_2), shift(i_2), facecolor='b', edgecolors='white', s=100)
                scatter.set_clip_on(False)
                ax.text(shift(j_2 + 2.5), shift(i_2 + 2.5), 'B', fontsize=24, color='white', path_effects=path_effects)
                fig.tight_layout()
            # plt.suptitle(f'Dist({key1}) Mean({key2}) Var({key3})')
            Path('./baselines').mkdir(exist_ok=True)
            [key1_p, key2_p, key3_p] = [key.replace('<', '-lt-').replace('=', '-eq-').replace('>', '-gt-') for key in [key1, key2, key3]]
            plt.savefig(f'./baselines/{key1_p} {key2_p} {key3_p}.png', dpi=300)

# save map with no A/B but only origin
plt.cla()
fig, axs = plt.subplots(1, 1)
path_effects = [pe.withStroke(linewidth=4, foreground="black")]
axs.axis('off')
axs.imshow(mapGrid, cmap='plasma', interpolation='bilinear')
axs.margins(x=100, y=100)
axs.scatter(shift(origin[1]), shift(origin[0]), c='r', edgecolors='white', s=100)
fig.tight_layout()
plt.savefig(f'./baselines/origin.png', dpi=300)
