# %%
import json
import s2sphere
import staticmaps

# get timeGridInfo.json
# bounds are (.topLeft.lat, .topLeft.lon), (topRight.lat, topRight.lon), (bottomRight.lat, bottomRight.lon), (bottomLeft.lat, bottomLeft.lon)

with open('timeGridInfo.json', 'r') as f:
    timeGridInfo = json.load(f)


context = staticmaps.Context()
context.set_tile_provider(staticmaps.tile_provider_CartoNoLabels)
context.add_bounds(
    staticmaps.parse_latlngs2rect(
        f"{timeGridInfo['topLeft']['lat']},{timeGridInfo['topLeft']['lon']} {timeGridInfo['bottomRight']['lat']},{timeGridInfo['bottomRight']['lon']}"
    )
)

# %%
image = context.render_pillow(1024, 1024)
image.save('map.png')
