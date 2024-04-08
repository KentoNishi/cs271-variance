import sys
import os
import json
from datetime import datetime

import math
import random
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns
from scipy.interpolate import RegularGridInterpolator, Rbf

from skimage import io
from PIL import Image, ImageDraw, ImageFont
import imageio

with open('means.json', 'r') as f:
    D = np.array(json.load(f))

with open('variances.json', 'r') as f:
    V = np.array(json.load(f))


bounds = [
    42.36020227811244,
    -71.13409264574024,
    42.383850169141745,
    -71.10504224250766 
] # S, W, N, E
origin = [42.36340914857679, -71.12589555981565]
origin_on_mesh = [(origin[0]-bounds[0])/(bounds[2]-bounds[0]), (origin[1]-bounds[1])/(bounds[3]-bounds[1])]
xo, yo = origin_on_mesh[1], 1-origin_on_mesh[0]

N = 100
lat_span = np.linspace(bounds[0], bounds[2], N)
long_span = np.linspace(bounds[1], bounds[3], N)
lats, longs = np.meshgrid(lat_span, long_span)


# Construct square and transformed meshes according to distance matrix
def construct_meshes():
    mesh = np.zeros((N,N,2))
    xx = []
    yy = []
    for i in range(N):
        for j in range(N):
            x, y = .01*(i+1) , .01*(j+1)
            mesh[i,j] = [x, y]
            xx.append(x)
            yy.append(y)
    
    dist_to_longest = 0
    time_to_longest = 0
    for i in range(N):
        for j in range(N):
            if D[i,j] > time_to_longest:
                time_to_longest = D[i,j]
                dist_to_longest = ((mesh[i,j][0])**2 + (mesh[i,j][1])**2)**(1/2)

    D1M = dist_to_longest/time_to_longest
            
    transformed_mesh = np.zeros((N,N, 2))
    xxt = []
    yyt = []
    for i in range(N):
        for j in range(N):
            d = D[i,j] * D1M
            x, y = mesh[i, j]
            a = math.atan2(y-yo, x-xo)
            xt, yt = xo + d*np.cos(a), yo + d*np.sin(a)
            transformed_mesh[i,j] = [xt, yt]
            xxt.append(xt)
            yyt.append(yt)

    return mesh, transformed_mesh, D1M, xx, yy, xxt, yyt

M, M_T, D1M, xx, yy, xxt, yyt = construct_meshes();



def plot_mesh(mesh, ax):
    xx = []
    yy = []
    for i in range(N):
        for j in range(N):
            xx.append(mesh[i,j][0])
            yy.append(mesh[i,j][1])


    ax.scatter(xx, 1-np.array(yy)) 
    ax.scatter(xo, 1-np.array(yo), color='red')
    return;

fig, axs = plt.subplots(1,3,figsize=(28,6))
axs[0].set_title('Original Mesh')
axs[0].grid(True)
plot_mesh(M, axs[0])
axs[1].set_title('Morphed Mesh')
axs[1].grid(True)
plot_mesh(M_T, axs[1])
sns.heatmap(D, ax = axs[2])
plt.savefig('images/meshes.png')
plt.show()



##
## Warp Image according to deformed mesh
##

minutesPerRing = int(sys.argv[1])
image = io.imread('images/isoerine.png');
r, c = image.shape[0], image.shape[1]
matchScale = "true"
dist_ring = D1M * minutesPerRing

#distance formula
def dist(x1,y1,x2,y2):
    return ((x1-x2)**2+(y1-y2)**2)**0.5

#l2 norm formula (distance from vector)
def L2(x, y):
    if x == 0 and y == 0:
        return [0, 0]
    mag = (x**2+y**2)**0.5
    return [x/mag, y/mag]

#memoize function (does things faster)
def memoize(func):
    cache = dict()
    
    def memoized_func(*args):
        if args in cache:
            return cache[args]
        result = func(*args)
        cache[args] = result
        return result
    
    return memoized_func

unit = "minute"
convertedRings = minutesPerRing
if convertedRings%60 == 0:
    convertedRings = convertedRings/60
    unit = "hour"
if convertedRings != 1:
    unit = unit+"s"
legendText = "Contour Scale: "+str(int(convertedRings))+" "+unit

dd = [dist(xx[i],yy[i],xo,yo) for i in range(N**2)]
dt = [dist(xxt[i],yyt[i],xo,yo) for i in range(N**2)]

#interpolates the distance for points not specifically written
interpType= 'linear'
UnwarpedInterpolater = Rbf(xxt,yyt,dd, function = interpType)
WarpedInterpolater = Rbf(xx,yy,dt, function = interpType)


def deform_image():
    X = np.zeros((r,c,4),dtype=np.uint8)
    for i in range(c):
        for j in range(r):
            o = j/r
            p = i/c
            dist_current = dist(p,o,xo,yo) #CHASE: myabe swtich
            
            # if currentDist < 0.002: # assumes origin is at center
            #     color = [255,0,0,255]
            dist_unwarped = UnwarpedInterpolater(1-p,o)
            normalized = L2(p-xo,o-yo)
            dist_map = dist_unwarped
            xu, yu = dist_map * normalized[0] + xo, dist_map * normalized[1] + yo
        
            if xu < 0 or xu > 1 or yu < 0 or yu > 1:
                color = [255,255,255,0]
            else:
                dist_warped = WarpedInterpolater(1-xu,yu)

                x_scaled, y_scaled = int(xu*(r-1)), int(yu*(c-1))

                color = image[x_scaled][y_scaled]
                if dist_current % dist_ring < 0.002:
                    color = [(color[0]+128)/2,(color[1]+128)/2,(color[2]+128)/2,255]
                X[j][i][0] = color[0]
                X[j][i][1] = color[1]
                X[j][i][2] = color[2]
                X[j][i][3] = color[3] # Alpha value
    img = Image.fromarray(X)
    draw = ImageDraw.Draw(img)
    img.save('images/warped_map.png')

deform_image()