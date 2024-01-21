import re
import numpy as np
from pyhdf.SD import SD, SDC
import re
import pyproj   
import glob

from netCDF4 import Dataset

def get_lonlat(dire):
   hdf = SD(dire, SDC.READ)
   data2D = hdf.select("sur_refl_b01")
   data = data2D[:,:].astype(np.float64)
   fattrs = hdf.attributes(full=1)
   ga = fattrs["StructMetadata.0"]
   gridmeta = ga[0]

   ul_regex = re.compile(r'''UpperLeftPointMtrs=\(
                                  (?P<upper_left_x>[+-]?\d+\.\d+)
                                  ,
                                  (?P<upper_left_y>[+-]?\d+\.\d+)
                                  \)''', re.VERBOSE)
   match = ul_regex.search(gridmeta)
   x0 = np.float(match.group('upper_left_x')) 
   y0 = np.float(match.group('upper_left_y')) 

   lr_regex = re.compile(r'''LowerRightMtrs=\(
                               (?P<lower_right_x>[+-]?\d+\.\d+)
                               ,
                               (?P<lower_right_y>[+-]?\d+\.\d+)
                               \)''', re.VERBOSE)
   match = lr_regex.search(gridmeta)
   x1 = np.float(match.group('lower_right_x')) 
   y1 = np.float(match.group('lower_right_y')) 
   ny, nx = data.shape
   xinc = (x1 - x0) / (nx+1) # +1 for non overlapping grid
   yinc = (y1 - y0) / (ny+1)
   #
   x = np.linspace(x0, x0 + xinc*nx, nx)
   y = np.linspace(y0, y0 + yinc*ny, ny)
   xv, yv = np.meshgrid(x, y)
   #
   D = {"proj":"sinu", "R":6371007.181, "nadgrids":"null"}
   sinu = pyproj.Proj("+proj=sinu +R=6371007.181 +nadgrids=@null +wktext")
   wgs84 = pyproj.CRS(4326)
   lat, lon= pyproj.Transformer.from_proj(sinu, wgs84).transform(xv, yv)
   hdf.end()
   return lon, lat

dire = "/datosfreyja/d1/GDATA/MODIS_PANTANAL/RAW/"
dfile = dire + "MOD09A1.A2003249.{0}.061.*"

outputdir = dire.replace("RAW", "")

def nctile_lonlat(tile, dfile, outputdir):
   dfile = glob.glob(dfile.format(tile))[0]
   lon, lat = get_lonlat(dfile)
   print(np.min(lon), np.max(lon))
   print(np.min(lat), np.max(lat))
  
   foo = Dataset(f"{outputdir}{tile}_grid.nc", "w")
   foo.createDimension('lat', lat.shape[0])
   foo.createDimension('lon', lat.shape[1])

   lonattr = {"standard_name":"longitude",
           "long_name":"Longitude",
           "units":"degrees_east",
           }
   latattr = {"standard_name":"latitude",
           "long_name":"Latitude",
           "units":"degrees_north"
           }

   nclon = foo.createVariable('lon', np.float64, ('lat','lon'), zlib = True)
   for nattr in lonattr.keys():
       nclon.setncattr(nattr, lonattr[nattr])
   nclon[:] = lon[:]

   nclat = foo.createVariable('lat', np.float64, ('lat','lon'), zlib = True)
   for nattr in latattr.keys():
       nclat.setncattr(nattr, latattr[nattr])
   nclat[:] = lat[:]
   foo.sync()
   foo.close()

##########################

dire = "/datosfreyja/d1/GDATA/MODIS_PANTANAL/RAW/"
dfile = dire + "MOD09A1.A2003249.{0}.061.*"

outputdir = dire.replace("RAW", "")


for tile in ["h12v10", "h12v11"]:
    nctile_lonlat(tile, dfile, outputdir)

