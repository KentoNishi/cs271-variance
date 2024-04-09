# %%
import json
import mpu
import copy
from tqdm import tqdm
from functools import cmp_to_key
import numpy as np

with open('meanTimeGrid.json', 'r') as f:
    meanTimeGrid = json.load(f)
with open('varianceTimeGrid.json', 'r') as f:
    varianceTimeGrid = json.load(f)
with open('timeGridInfo.json', 'r') as f:
    timeGridInfo = json.load(f)
origin = (timeGridInfo['origin']['lat'], timeGridInfo['origin']['lon'])
origin_x = round((origin[0] - 42.383850169141745) / (42.36020227811244 - 42.383850169141745) * 100)
origin_y = round((origin[1] - -71.13409264574024) / (-71.10504224250766 + 71.13409264574024) * 100)
# originMean = meanTimeGrid[origin_x][origin_y]
# originVariance = varianceTimeGrid[origin_x][origin_y]

# %%

# categorized = 3d dict with keys of each dimension being "A<B", "A=B", "A>B"
# each value is a list of tuples (p_1, p_2)

factor = 2

empty = {
    "A<B": [],
    "A=B": [],
    "A>B": [],
}
categorized = copy.deepcopy(empty)
for key in categorized:
    categorized[key] = copy.deepcopy(empty)
    for key_1 in categorized[key]:
        categorized[key][key_1] = copy.deepcopy(empty)
        for key_2 in categorized[key][key_1]:
            categorized[key][key_1][key_2] = []
empty = copy.deepcopy(categorized)

t = tqdm(total=(100 // (factor))**2)

for i_1 in range(0, 100, factor):
    for j_1 in range(0, 100, factor):
        for i_2 in range(round(i_1 + factor), 100, factor):
            for j_2 in range(round(j_1 + factor), 100, factor):
                p_1 = (
                    42.383850169141745 + (42.36020227811244 - 42.383850169141745) * (i_1) / (((100 // factor) - 1) * factor),
                    -71.13409264574024 + (-71.10504224250766 + 71.13409264574024) * (j_1) / (((100 // factor) - 1) * factor),
                )
                p_2 = (
                    42.383850169141745 + (42.36020227811244 - 42.383850169141745) * (i_2) / (((100 // factor) - 1) * factor),
                    -71.13409264574024 + (-71.10504224250766 + 71.13409264574024) * (j_2) / (((100 // factor) - 1) * factor),
                )
                m_1, v_1 = meanTimeGrid[i_1][j_1], varianceTimeGrid[i_1][j_1]
                m_2, v_2 = meanTimeGrid[i_2][j_2], varianceTimeGrid[i_2][j_2]
                d_1 = mpu.haversine_distance(origin, p_1)
                d_2 = mpu.haversine_distance(origin, p_2)
                d_d = mpu.haversine_distance(p_1, p_2)
                if d_d < 0.5 or d_1 < 0.5 or d_2 < 0.5:
                    continue
                thresh_1 = 0.25
                thresh_2 = 2.5
                thresh_3 = 2.5
                def comp(x, y):
                    if abs(x[0] - y[0]) >= thresh_1:
                        return x[0] - y[0]
                    if abs(x[1] - y[1]) >= thresh_2:
                        return x[1] - y[1]
                    return x[2] - y[2]
                [t_1, t_2] = sorted([(d_1, m_1, v_1, i_1, j_1), (d_2, m_2, v_2, i_2, j_2)], key=cmp_to_key(comp))
                key_0 = "A=B" if abs(t_1[0] - t_2[0]) < thresh_1 else "A<B" if t_1[0] < t_2[0] else "A>B"
                key_1 = "A=B" if abs(t_1[1] - t_2[1]) <= thresh_2 else "A<B" if t_1[1] < t_2[1] else "A>B"
                key_2 = "A=B" if abs(t_1[2] - t_2[2]) <= thresh_3 else "A<B" if t_1[2] < t_2[2] else "A>B"
                if (
                    (key_0 != "A=B" and abs(t_1[0] - t_2[0]) < thresh_1) or
                    (key_1 != "A=B" and abs(t_1[1] - t_2[1]) < thresh_2) or
                    (key_2 != "A=B" and abs(t_1[2] - t_2[2]) < thresh_3)
                ):
                    continue
                categorized[key_0][key_1][key_2].append(((p_1, (t_1[3], t_1[4])), (p_2, (t_2[3], t_2[4]))))
        t.update(1)

info = {
    "origin": origin,
#     "originMean": originMean,
#     "originVariance": originVariance,
    "originX": origin_x,
    "originY": origin_y,
    "categoriesIndexOrder": ["distance", "mean", "variance"],
}

# sort each triplet of keys by maximizing the sum of distances between the items' keys for keys which are not "A=B" for each pair
for key1 in categorized:
    for key2 in categorized[key1]:
        for key3 in categorized[key1][key2]:
            if len(categorized[key1][key2][key3]) == 0:
                continue
            dists_1 = [
                mpu.haversine_distance(x[0][0], x[1][0]) for x in categorized[key1][key2][key3]
            ]
            mean_1, std_1 = np.mean(dists_1), np.std(dists_1)
            dists_2 = [
                abs(meanTimeGrid[x[0][1][0]][x[0][1][1]] - meanTimeGrid[x[1][1][0]][x[1][1][1]]) for x in categorized[key1][key2][key3]
            ]
            mean_2, std_2 = np.mean(dists_2), np.std(dists_2)
            dists_3 = [
                abs(varianceTimeGrid[x[0][1][0]][x[0][1][1]] - varianceTimeGrid[x[1][1][0]][x[1][1][1]]) for x in categorized[key1][key2][key3]
            ]
            mean_3, std_3 = np.mean(dists_3), np.std(dists_3)
            
            def comp(x):
                i_1, j_1 = x[0][1]
                i_2, j_2 = x[1][1]
                dist_1 = (
                    (mpu.haversine_distance(x[0][0], x[1][0]) if key1 != "A=B" else mean_1) - mean_1
                ) / (std_1 if std_1 != 0 else 1)
                dist_2 = (
                    (abs(meanTimeGrid[i_1][j_1] - meanTimeGrid[i_2][j_2]) if key2 != "A=B" else mean_2) - mean_2
                ) / (std_2 if std_2 != 0 else 1)
                dist_3 = (
                    (abs(varianceTimeGrid[i_1][j_1] - varianceTimeGrid[i_2][j_2]) if key3 != "A=B" else mean_3) - mean_3
                ) / (std_3 if std_3 != 0 else 1)
                return (dist_1 + dist_2 + dist_3) / (
                    (
                        (1 if key1 != "A=B" else 0) + (1 if key2 != "A=B" else 0) + (1 if key3 != "A=B" else 0)
                    )
                    or 1
                )

            categorized[key1][key2][key3].sort(key=comp, reverse=True)

json.dump({
    "info": info,
    "categories": categorized,
}, open('categorizedGpsCoordinates.json', 'w'))

# save best gps coordinates for each category in json
keys = ["A=B", "A<B", "A>B"]

def remove_empty_elements(d):
    """recursively remove empty lists, empty dicts, or None elements from a dictionary"""

    def empty(x):
        return x is None or x == {} or x == []

    if not isinstance(d, (dict, list)):
        return d
    elif isinstance(d, list):
        return [v for v in (remove_empty_elements(v) for v in d) if not empty(v)]
    else:
        return {k: v for k, v in ((k, remove_empty_elements(v)) for k, v in d.items()) if not empty(v)}

best = copy.deepcopy(empty)
for key1 in keys:
    for key2 in keys:
        for key3 in keys:
            items = categorized[key1][key2][key3]
            if len(items) > 0:
                best[key1][key2][key3] = items[0][0][0]

json.dump(remove_empty_elements(best), open('surveyGpsCoordinates.json', 'w'))

