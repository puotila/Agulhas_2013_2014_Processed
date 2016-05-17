#!/usr/bin/env python
"""
Read antload ice thickness data from mat files to a python class.
Then map to an orca025 grid with monthly frequency to ease comparison
with NEMO model simulations.
"""

import os
import sys
import gzip
import cPickle
from datetime import datetime, timedelta
import numpy as np
from scipy.io import loadmat
import scipy.io.netcdf as nc
import glob
sys.path.append(os.path.join(os.getenv('HOME'),'python/GeoInterpolate/'))
from GeoInterpolate_f90r import geointerpolate_f90r as gi

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
        self.x     = [] # closest model grid index (ix,iy)
        self.y     = [] # closest model grid index (ix,iy)
        self.vname = 'sit' # sea ice thickness

    def selectData(self,vname,raw,pro):
        """ Select valid values by masking out invalid ones
        """
        out = np.ma.masked_where((pro['selectgoodth']==0)|\
                                 (pro['selectrammings']==1)|\
                                 (raw['Lamp']<=1170)|\
                                 (raw['Hice2']<0),\
                                  raw[vname])
        return out

    def getSegment(self,vari,pro,func=np.ma.mean,segkey='segments100m'):
        out = np.ma.array([func(vari[pro[segkey][i][0]:pro[segkey][i][1]]) \
                                            for i in range(pro[segkey].shape[0])])
        return out[np.where(out.mask==False)]

    def readMatFile(self,fidx):
        date0 = datetime(1970,1,1,0) # UTC
        raw  = loadmat("mittaus%02d.mat" % fidx)
        pro  = loadmat("processed%d.mat" % fidx)
        hice2 = self.selectData('Hice2',raw,pro)
        lat = self.selectData('Latitude',raw,pro)
        lon = self.selectData('Longitude',raw,pro)
        timestamp = self.selectData('Timestamp',raw,pro)
        # average valid data in 100m segments
        self.data = self.getSegment(hice2,pro)
        self.lat = self.getSegment(lat,pro)
        self.lon = self.getSegment(lon,pro)
        time = self.getSegment(timestamp,pro)
        self.dates = [date0 + timedelta(t/86400,t%86400) for t in time]
        min_i = gi.nearest_neighbour_indices(self.lon,self.lat,\
                                       self.grdlon,self.grdlat,\
                                               self.gx,self.gy,\
                                                  len(self.lon))
        self.x, self.y = min_i[:,0]-1, min_i[:,1]-1

    def readModelGrid(self,lat_lim=-55.,\
                      grdfile="coordinates_ORCA025.nc"):
        fp = nc.netcdf_file(grdfile)
        lat = np.array(fp.variables['nav_lat'][:])
        idx = np.where(lat<-55.)
        lon = np.array(fp.variables['nav_lon'][:])
        self.grdlat = lat[:idx[0].max()+1,:]
        self.grdlon = lon[:idx[0].max()+1,:]
        fp.close()
        self.gx, self.gy = self.grdlon.shape

if __name__ == "__main__":
    fidx = int(sys.argv[1])
    cgzfile = "antload%02d.cpickle.gz" % fidx
    antload = Antload()
    antload.readModelGrid()
    if not os.path.exists(cgzfile):
        sys.stdout.write("Starting %02d ...\n" % fidx)
        sys.stdout.flush()
        antload.readMatFile(fidx)
        # save
        save_zipped_pickle(antload,cgzfile)
    # load
    antload = load_zipped_pickle(cgzfile)
    sys.stdout.write("%s processed!\n" % fidx)
    sys.stdout.flush()
    print "Finnished!"
