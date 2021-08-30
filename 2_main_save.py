import sys
sys.path.append("library")
from lib_MODISlonlat import nctile_lonlat
from lib_extractMODIS import finalFile, jdtodatestd
import configparser
import tqdm
import glob
import numpy as np

D = {}
D["h13v12"] = [0, 2400, 0, 2400]
nx = 2400
ny = 2400
"""
Example Pantanal
D["h12v10"] = [1100, 2400, 800, 2000]
D["h12v11"] = [0, 500, 800, 2000]

nx = 2000-800
ny = 2400-1100+500
"""

tiles = list(D.keys())
    
#############################
# 2. Get longitude/latitude #
#############################
config=configparser.ConfigParser()
config.read("config.def")
output=config.get("OverAll", "output") 

# plus general et chercher le premier avec glob

dfile = output +"/RAW/"+"MOD09A1.A2021209.{0}.061.*" 
final_output = output +"/"
for tile in tiles:
    nctile_lonlat(tile, dfile, final_output)

##############################
# 3. Save into a netCDF file #
##############################

# Get the MODIS files -> List of date
ff = glob.glob(output+f"/RAW/MOD09A1.*{tiles[0]}*")
ff = [f.split("/")[-1].split(".")[1] for f in ff]

date = [jdtodatestd(f[1:]) for f in ff]
dd = np.argsort(date)
ff = [ff[ind] for ind in dd]


# The following has been constructed to join two images
# It seems to be working when there is only one image
# Need to be rework if there are more images 
# Or perform for single images and then join the files.

finalFile(ff, output +"/RAW/", D, nx, ny)

 
