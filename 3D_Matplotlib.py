import os, sys
from osgeo import gdal
import numpy as np

import scipy as sp
import scipy.interpolate

from mpl_toolkits.mplot3d.axes3d import *
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.mlab import griddata

import matplotlib.dates as dates
import matplotlib.ticker as ticker
import datetime
from datetime import datetime, time,date



DEM_path = "E:\\Geo\\GermanyDGM1\\dgm1_5meter.img"
Track_path = "E:\\_SOSE2017\\PIG\\Python and ArcGIS\\ArcGIS-Data - matplotlib\\track_reprojected.shp"
field_Name = "datetime"
time_Format = '%Y-%m-%dT%H:%M:%SZ'



# Helper function 
# converts dates in number format
# and returns the time portion of the date
def format_date(x, pos=None):
     return dates.num2date(x).strftime('%H:%M:%S') #use FuncFormatter to format dates

# This function reads raster image
# passed as a parameter
# and extract elevation values
# and surfaceplot the image
def plot_dem(path):
    #load the raster inmage
    Image  = gdal.Open(DEM_path)

    #Get the first band
    Band   = Image.GetRasterBand(1) # 1 based, for this example only the first
    NoData = Band.GetNoDataValue()  # this might be important later

    # Get raster extent
    nBands = Image.RasterCount      # how many bands, to help you loop
    nRows  = Image.RasterYSize      # how many rows
    nCols  = Image.RasterXSize      # how many columns

    RowRange = range(0,nRows,2000)
    Cells    = range(0,nCols,2000)

    # Arrays to hold the values for plotting
    x=[]
    y=[]
    z=[]

    # iterating through all rows 
    for ThisRow in RowRange:

        # Read data line by line is better for performance on large datasets
        ThisLine = Band.ReadAsArray(0,ThisRow,nCols,1).astype(np.float)

        # report every 100 lines
        if ThisRow % 100 == 0: 
            print "Scanning %d of %d" % (ThisRow,nRows)

        #iterating through cells and extracting coordinates and elevation values
        for ThisCell in Cells:
            Val = ThisLine[0].item(ThisCell)
            x.append(ThisRow)
            y.append(ThisCell)
            z.append(Val)
                
    # setting interpolation variables for constructing the surface
    spline = sp.interpolate.Rbf(x,y,z,function='thin-plate')
    xi = np.linspace(min(x), max(x))
    yi = np.linspace(min(y), max(y))
    X, Y = np.meshgrid(xi, yi)
    # interpolation
    Z = spline(X,Y)

    fig = plt.figure()
    ax = Axes3D(fig)
    ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=cm.jet,linewidth=1, antialiased=True)
    plt.show()


# This function reads the vector track
# passed as a parameter
# also taked the field name which holds the time
# in addition to the time format used
# extracts elevation values
# and surfaceplot the track in 3D cube
def plot_track(path, fieldName, timeFormat):
    # Reading the vector track
    shppath = Track_path
    driver = ogr.GetDriverByName('ESRI Shapefile')
    datasource = driver.Open(shppath,0)
    layer = datasource.GetLayer(0)

    f, axarr   = plt.subplots(1)

    # Arrays to hold the values for plotting
    X = []
    Y = []
    T = []

    # Iterating through features and etracting coordinates and time
    for feat in layer:
      pt = feat.geometry()
      x = pt.GetX()
      y = pt.GetY()

      #Get time value
      tim = feat.GetField(field_Name)

      # parsing time to object 
      tim1 = datetime.strptime(tim, time_Format)

      #Convert time to number of days
      tim3 = dates.date2num(tim1)

      #store values in plotting arrays
      X.append(x)
      Y.append(y)
      T.append(tim3)


    # plotting the figure with scatter3D
    fig = plt.figure()
    ax = Axes3D(fig)
    ax.scatter3D(X,Y,T,c=T,cmap=plt.cm.jet)  
    # setting the date format of the z axis to show H,m,S  
    ax.w_zaxis.set_major_formatter(ticker.FuncFormatter(format_date))
    plt.show()


# Main

plot_dem(DEM_path)
plot_track(Track_path, field_Name, time_Format)