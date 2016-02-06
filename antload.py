#!/usr/bin/env python
"""
Read antload ice thickness data from mat files to a python class.
Then map to an orca025 grid with monthly frequency to ease comparison
with NEMO model simulations.
"""

import sys
import gzip
import cPickle
from datetime import datetime, timedelta
import numpy as np
from scipy.io import loadmat
import scipy.io.netcdf as nc
import glob

# global functions
def save_zipped_pickle(obj, filename, protocol=-1):
    with gzip.open(filename, 'wb') as f:
        cPickle.dump(obj, f, protocol)

def load_zipped_pickle(filename):
    with gzip.open(filename, 'rb') as f:
        loaded_object = cPickle.load(f)
        return loaded_object

class Antload(object):
    def __init__(self):
        self.data  = []
        self.dates = []
        self.lat   = []
        self.lon   = []
        self.x     = [] # closest model grid index
        self.y     = [] # closest model grid index
        self.vname = 'sit' # sea ice thickness

    def readMatFile(self,filename):
        date0,data = datetime(1970,1,1,0),[] # UTC
        raw  = loadmat(filename)
        for i,t in enumerate(raw['Timestamp']):
            date = date0 + timedelta(t[0]/86400,t[0]%86400)
            self.dates.append(date)
            if i%1000.==0:
                print "Processed %i records out of %i" % \
                     (i,len(raw['Timestamp']))
                sys.stdout.flush()
            data.append(raw['Hice'][i][0])
            lat = raw['Latitude'][i][0]
            lon = raw['Longitude'][i][0]
            self.lat.append(lat)
            self.lon.append(lon)
            # closest model orca025 grid point
            dst   = self.haversine(self.grdlon,self.grdlat,lon,lat)
            min_i = np.where(dst==np.min(dst))
            self.x.append(min_i[0][0])
            self.y.append(min_i[1][0])
        # consider ice thicknesses greater than 3m unrealiable
        self.data = np.ma.array(data,mask=data>3.)

    def readFiles(self,fpat='mittaus*.mat'):
        for fn in sorted(glob.glob(fpat)):
            self.readMatFile(fn)

    def readModelGrid(self,lat_lim=-55.,\
                      grdfile="/home/uotilap/tiede/CMCC/analyses/coordinates.nc"):
        fp = nc.netcdf_file(grdfile)
        lat = np.array(fp.variables['nav_lat'][:])
        idx = np.where(lat<-55.)
        lon = np.array(fp.variables['nav_lon'][:])
        self.grdlat = lat[:idx[0].max()+1,:]
        self.grdlon = lon[:idx[0].max()+1,:]
        fp.close()

    def haversine(self,lon1,lat1,lon2=None,lat2=None,REarth=6372.795e3):
        """
        computes distance btw. lat,lon points in [m]
        if lon1,lat1 is a matrix then matrix of distances from
        point lon2,lat2 is returned
        """
        if lon2 is None: lon2 = self.lon2
        if lat2 is None: lat2 = self.lat2
        D2R = 57.2957795130823
        dlon = (lon1 - lon2) / D2R
        dlat = (lat1 - lat2) / D2R
        a1  = np.power(np.sin(dlat/2),2)
        a2  = np.cos(lat2/D2R)
        a2 *= np.cos(np.float32(lat1)/D2R)
        a2 *= np.power(np.sin(dlon/2),2)
        a   = a1 + a2
        a[np.where(a<0.0)] = 0.0
        a[np.where(a>1.0)] = 1.0
        c = 2 * np.arctan2(np.sqrt(a),np.sqrt(1-a))
        #print "a=[%f,%f]" % (np.min(a),np.max(a))
        return c*REarth

if __name__ == "__main__":
    cgzfile = 'antload.cpickle.gz'
    antload = Antload()
    antload.readModelGrid()
    for fn in sorted(glob.glob('mittaus*.mat')):
        sys.stdout.write("Starting %s ...\n" % fn)
        sys.stdout.flush()
        antload.readMatFile(fn)
        # save
        save_zipped_cpickle(antload,cgzfile)
        # load
        antload = load_zipped_cpickle(cgzfile)
        sys.stdout.write("%s processed!\n" % fn)
        sys.stdout.flush()
    print "Finnished!"
