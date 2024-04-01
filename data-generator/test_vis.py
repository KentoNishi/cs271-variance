# %%
# read in ./meanTimeGrid.json, a 99x99 grid of floats
# and visualize it with matplotlib

import json
import numpy as np
import matplotlib.pyplot as plt

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
