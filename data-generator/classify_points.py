# %%
import json
import mpu
import copy
from tqdm import tqdm
from functools import cmp_to_key

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

factor = 4

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

# t = tqdm(total=(100 // (factor))**4)

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
                if d_d < 0.5:
                    # t.update(1)
                    continue
                def comp(x, y):
                    if abs(x[0] - y[0]) >= 0.1:
                        return x[0] - y[0]
                    if abs(x[1] - y[1]) >= 2.5:
                        return x[1] - y[1]
                    return x[2] - y[2]
                [t_1, t_2] = sorted([(d_1, m_1, v_1, i_1, j_1), (d_2, m_2, v_2, i_2, j_2)], key=cmp_to_key(comp))
                key_0 = "A=B" if abs(t_1[0] - t_2[0]) < 0.1 else "A<B" if t_1[0] < t_2[0] else "A>B"
                key_1 = "A=B" if abs(t_1[1] - t_2[1]) <= 2.5 else "A<B" if t_1[1] < t_2[1] else "A>B"
                key_2 = "A=B" if abs(t_1[2] - t_2[2]) <= 2.5 else "A<B" if t_1[2] < t_2[2] else "A>B"
                categorized[key_0][key_1][key_2].append(((p_1, (t_1[3], t_1[4])), (p_2, (t_2[3], t_2[4]))))
                # t.update(1)

info = {
    "origin": origin,
#     "originMean": originMean,
#     "originVariance": originVariance,
    "originX": origin_x,
    "originY": origin_y,
    "categoriesIndexOrder": ["distance", "mean", "variance"],
}

json.dump({
    "info": info,
    "categories": categorized,
}, open('categorizedGpsCoordinates.json', 'w'))
