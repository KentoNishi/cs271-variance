# %%
# read in ./meanTimeGrid.json, a 99x99 grid of floats
# and visualize it with matplotlib

import json
import numpy as np
import matplotlib.pyplot as plt
import random
from pathlib import Path
import matplotlib.patheffects as pe


# read in the json file
with open('meanTimeGrid.json', 'r') as f:
    meanTimeGrid = json.load(f)

# convert the json object to a numpy array
meanTimeGrid = np.array(meanTimeGrid)

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

# get the origin
origin = categorized['info']['originX'], categorized['info']['originY']
keys = ["A=B", "A<B", "A>B"]

for key1 in keys:
    for key2 in keys:
        for key3 in keys:
            items = categorized['categories'][key1][key2][key3]
            if len(items) < 4:
                continue
            sampled_items = [items[0]] # [:4]
            plt.cla()
            fig, axs = plt.subplots(1, 1) # plt.subplots(2, 2)
            for (((p_1, (i_1, j_1)), (p_2, (i_2, j_2))), ax) in zip(sampled_items, [axs]):
                # plt.cla()
                # plt.imshow(varianceTimeGrid, cmap='viridis', interpolation='bilinear')
                # plt.scatter(origin[1], origin[0], c='r', edgecolors='white')
                # plt.scatter(j_1, i_1, c='b', edgecolors='white')
                # plt.scatter(j_2, i_2, c='b', edgecolors='white')
                # plt.show()
                path_effects = [pe.withStroke(linewidth=4, foreground="black")]
                ax.axis('off')
                ax.imshow(meanTimeGrid, cmap='plasma', interpolation='bilinear')
                ax.margins(x=100, y=100)
                ax.scatter(origin[1], origin[0], c='r', edgecolors='white', s=100)
                scatter = ax.scatter(j_1, i_1, facecolor='b', edgecolors='white', s=100)
                scatter.set_clip_on(False)
                ax.text(j_1 + 2.5, i_1 + 3, 'A', fontsize=24, color='white', path_effects=path_effects)
                scatter = ax.scatter(j_2, i_2, facecolor='b', edgecolors='white', s=100)
                scatter.set_clip_on(False)
                ax.text(j_2 + 2.5, i_2 + 2.5, 'B', fontsize=24, color='white', path_effects=path_effects)
                fig.tight_layout()
            # plt.suptitle(f'Dist({key1}) Mean({key2}) Var({key3})')
            Path('./images').mkdir(exist_ok=True)
            [key1_p, key2_p, key3_p] = [key.replace('<', ' lt ').replace('=', ' eq ').replace('>', ' gt ') for key in [key1, key2, key3]]
            plt.savefig(f'./images/{key1_p}_{key2_p}_{key3_p}.png')
