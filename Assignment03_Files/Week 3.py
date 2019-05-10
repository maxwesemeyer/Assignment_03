# ############################################################################################################# #
# Raw-example for a basic script to be executed in python. The format is only a recommendation and everyone is  #
# encouraged to modify the scripts to her/his own needs.                                                        #
# (c) Matthias Baumann, Humboldt-Universität zu Berlin, 4/15/2019                                               #
# ####################################### LOAD REQUIRED LIBRARIES ############################################# #
import time
import os
import re
import pandas as pd
import math
import geopandas
from shapely.geometry import box
import numpy as np
import gdal
# ####################################### SET TIME-COUNT ###################################################### #
starttime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("Starting process, time: " + starttime)
print("")
# ####################################### FOLDER PATHS & global variables ##################################### #
datapath = "C:/Users/Maximus/PycharmProjects/untitled/Assignment03_Files/"
files = os.listdir(datapath)
buff_m = 100
# ####################################### FUNCTIONS ########################################################### #
def getRasterExtent(list_of_files, data_path):
    xmins = []
    ymins = []
    xmaxs = []
    ymaxs = []
    projections = []

    for f in list_of_files:
        if re.match(".*\\.[tT][iI][fF]{1,2}$", f):
            raster = gdal.Open(data_path + f)
            projections.append(raster.GetProjection())
            cols = raster.RasterXSize
            rows = raster.RasterYSize
            f_xmin, f_pwidth, f_xskew, f_ymax, f_yskew, f_pheight = raster.GetGeoTransform()
            xmins.append(f_xmin)
            xmaxs.append(f_xmin + (f_pwidth * cols))
            ymaxs.append(f_ymax)
            ymins.append(f_ymax + (f_pheight * rows))
            del raster
    for counter in range(0, 4):
        print(counter)
        if projections[counter] == projections[counter + 1]:
            print('projections match')
        else:
            print('Projections dont match')
    box_1 = box(xmins[0], ymins[0], xmaxs[0], ymaxs[0])
    box_2 = box(xmins[1], ymins[1], xmaxs[1], ymaxs[1])
    box_3 = box(xmins[2], ymins[2], xmaxs[2], ymaxs[2])
    box_4 = box(xmins[3], ymins[3], xmaxs[3], ymaxs[3])
    box_5 = box(xmins[4], ymins[4], xmaxs[4], ymaxs[4])
    intersecto = box_1.intersection(box_2)
    intersecto = intersecto.intersection(box_3)
    intersecto = intersecto.intersection(box_4)
    intersecto = intersecto.intersection(box_5)
    UL = list(intersecto.exterior.coords)[0]
    LR = list(intersecto.exterior.coords)[2]
    return [UL, LR]

# ####################################### PROCESSING ########################################################## #
boxes = getRasterExtent(files, data_path=datapath)
#print(boxes)
# ####################################### Task Group 3 ########################################################## #
UL = boxes[0]
LR = boxes[1]

stats = []
list_of_arrays = []
for f in files:
    if re.match(".*\\.[tT][iI][fF]{1,2}$", f):
        ds = gdal.Open(datapath+f)
        gt = ds.GetGeoTransform()
        inv_gt = gdal.InvGeoTransform(gt)

        offset_ul = gdal.ApplyGeoTransform(inv_gt, UL[0], UL[1])

        offset_lr = gdal.ApplyGeoTransform(inv_gt, LR[0], LR[1])
        off_ulx, off_uly = map(int, offset_ul)
        off_lrx, off_lry = map(int, offset_lr)
        rows = off_lry - off_uly
        columns = off_lrx - off_ulx
        overlap_array = ds.ReadAsArray(off_ulx, off_uly, columns, rows)
        #calculate image statistics
        list_of_arrays.append(overlap_array)
        mean = overlap_array.mean()
        median = np.median(overlap_array)
        shape = overlap_array.shape
        min = overlap_array.min()
        max = overlap_array.max()
        range = max-min
        sd = overlap_array.std()
        stats.append({'image': f,'mean': mean, 'median': median, 'min': min,
                      'max': max, 'range': range, 'shape': shape, 'sd': sd})

#convert to Pandas DataFrame and create a year column using regex
image_statistics = pd.DataFrame(stats)

year = []
for i in image_statistics['image']:
    years = re.search("\d{4}", i).group()
    years = int(years)
    year.append(years)
image_statistics['year'] = pd.Series(year, index = image_statistics.index)



st_00_10 = list_of_arrays[0]-list_of_arrays[2]
print(st_00_10.mean())
st_10_18 = list_of_arrays[2]-list_of_arrays[4]
print(st_10_18.mean())
#print(np.asanyarray(list_of_arrays, dtype = np.float32))
#print(image_statistics.loc[image_statistics['year']==2000,'mean'])
image_statistics.to_csv(datapath+"image_stats.csv")
# ####################################### END TIME-COUNT AND PRINT TIME STATS################################## #
print("")
endtime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
print("--------------------------------------------------------")
print("start: " + starttime)
print("end: " + endtime)
print("")
