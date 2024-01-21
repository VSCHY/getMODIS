from netCDF4 import Dataset, date2num, num2date
import glob
import numpy as np
import tqdm
import datetime

# Directions and tiles
dire = "/datosfreyja/d1/GDATA/MODIS_PANTANAL/"
tiles = ["h12v10", "h12v11"]

# Get the MODIS files -> List of date
ff = glob.glob(dire+f"RAW/MOD09A1.*{tiles[0]}*")
ff = [f.split("/")[-1].split(".")[1] for f in ff]

def get_dfile(date, tile):
    d = dire+"RAW/MOD09A1.{0}.{1}*"
    print(d.format(date, tile))
    return glob.glob(d.format(date, tile))[0]

def jdtodatestd (jdate):
    fmt = '%Y%j'
    datestd = datetime.datetime.strptime(jdate, fmt).date()
    return(datestd)

# Limits of Pantanal over both grid
D = {}
D["h12v10"] = [1100, 2400, 600, 2000]
D["h12v11"] = [0, 500, 600,2000]

#D["h12v10"] = [0, 2400, 0, 2400]
#D["h12v11"] = [0, 2400, 0,2400]

nx = 2000-600
ny = 2400-1100+500

#nx = 2400
#ny = 2400*2

class finalFile:
    def __init__(self, Ldate):
        self.d0 = datetime.date(2000,1,1)
        self.unit = "days since 2000-01-01"
        self.Ldate = Ldate
        self.ndate = len(Ldate)

        self.get_Dd(0)
        self.update_time()

        nc1 = Dataset(self.Dd[tiles[0]][0])
        self.varlist = list(nc1.variables.keys())
        nc1.close()

        #self.find_x_start()
        print("Initialize")
        self.initialize_file()
        print("Filling the file")
        self.fill_file() 
        print("Finalization")
        self.finalize()

    def get_Dd(self, ind):
        if len(glob.glob(dire+"RAW/MOD09A1.{0}*".format(self.Ldate[ind])))<2:
            print("Both images are not available", glob.glob(dire+"RAW/MOD09A1.{0}*".format(date)))
        else:
            self.Dd = {t:[get_dfile(self.Ldate[ind], t), dire+f"{t}_grid.nc" ] for t in tiles}

    def update_time(self):
        print("Check if both images are present for each date")
        Ldate = []
        for date in self.Ldate:
            if len(glob.glob(dire+"RAW/MOD09A1.{0}*".format(date)))<2:
                print("Both images are not availables:", date)
            else:
                Ldate.append(date)
        self.Ldate = Ldate
        self.ndate = len(Ldate)

    def initialize_file(self):
        dtime = [jdtodatestd(f[1:]) for f in self.Ldate]

        self.foo = Dataset(dire + f"MOD09A1_Pantanal_{dtime[0].month}-{dtime[0].year}_{dtime[-1].month}-{dtime[-1].year}.nc", "w")
        
        self.foo.createDimension("y", ny)
        self.foo.createDimension("x", nx)
        self.foo.createDimension("time",None)

        # list date2num 
        time_attr = {"standard_name":"time",
                "long_name":"Time axis",
                "calendar":"gregorian",
                "units":self.unit,
                "time_origin":self.unit.replace("days since ", "")
                }
        t = self.foo.createVariable("time", int, ('time'))
        for attrn in time_attr.keys():
            t.setncattr(attrn, time_attr[attrn])
        dtime = [jdtodatestd(f[1:]) for f in self.Ldate]

        t[:] = [(dt-self.d0).days for dt in dtime]# HERE
        #
        #########################
        #########################
        #

        # lon / lat
        nc = Dataset(self.Dd[tiles[0]][1], "r")
        for varn in ["lon", "lat"]:
           ovar = nc.variables[varn]
           nvar = self.foo.createVariable(varn, np.float64, ('y','x'), zlib = True)
           for attrn in ovar.ncattrs():
             if attrn != "_FillValue":
               attrv = ovar.getncattr(attrn)
               nvar.setncattr(attrn, attrv)
        nc.close()

        nc = Dataset(self.Dd[tiles[0]][0], "r")
        for varn in self.varlist:
           if varn[:11] == "surf_refl_b":
               NCFillValue = -28672
           else:
               NCFillValue = 0
           nvar = self.foo.createVariable(varn, np.float64, ('time','y', 'x'), zlib = True, fill_value=NCFillValue)
           ovar = nc.variables[varn]
           for attrn in ovar.ncattrs():
            if attrn != "_FillValue":
               attrv = ovar.getncattr(attrn)
               nvar.setncattr(attrn,attrv)
        nc.close()

    def insert_variables_grid(self,ind):
        self.get_Dd(ind)
        nj = 0
        for t in tiles:
            j0,j1,i0,i1 = D[t]
            if ind ==0:
               nc = Dataset(self.Dd[t][1], "r")
               for varn in ["lon", "lat"]:
                  self.foo.variables[varn][nj:nj+j1-j0, :i1-i0] = nc.variables[varn][j0:j1,i0:i1]
               nc.close()
                        
            nc = Dataset(self.Dd[t][0], "r")
            for varn in self.varlist:
                self.foo.variables[varn][ind,nj:nj+j1-j0, :i1-i0] = nc.variables[varn][j0:j1,i0:i1]
            nc.close()
            nj += j1-j0
    
    def find_x_start(self):
       nc0 = Dataset(self.Dd[tiles[0]][1], "r")
       nc1 = Dataset(self.Dd[tiles[1]][1], "r")
       j0,j1,i0,i1 = D[tiles[0]]
       print("h10", j0,j1,i0,i1)

       lat0 = nc0.variables["lat"][-1,i1]
       lon0 = nc0.variables["lon"][-1,i1]
       lat1 = nc1.variables["lat"][0,i1]
       lon1 = nc1.variables["lon"][0,i1]

       j0,j1,i0,i1 = D[tiles[1]]
       print("h11", j0,j1,i0,i1)

       print(lat0, lon0)
       print(lat1, lon1)


    def fill_file(self):
        for ind in range(self.ndate):
            print(f"{ind}/{self.ndate}")
            self.insert_variables_grid(ind)
            if (ind+1) % 10 == 0:
                self.foo.sync()
           
    def finalize(self):
        self.foo.sync()
        self.foo.close()

date = [jdtodatestd(f[1:]) for f in ff]
dd = np.argsort(date)
ff = [ff[ind] for ind in dd]

finalFile(ff)


