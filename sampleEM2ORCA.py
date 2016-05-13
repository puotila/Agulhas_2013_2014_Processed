#!/usr/bin/env python
"""
Sample ANTLOAD EM-measurements to ORCA025 grid
as multi-category ice distribution. Here we use
the default five categories, at first at least.
antload.py must be run before to know t,x,y
Measurements 2013-14 campaigns are used.
Save to netCDF.
"""

import sys
import glob
from datetime import datetime, timedelta
import numpy as np
import netCDF4 as nc
from netcdftime import utime
from antload import Antload, load_zipped_pickle

class obsIceThickDistr(Antload):
    def __init__(self,fno,grid='orca025',ncatice=5,hiceb=None):
        self.grid = 'orca025'
        self.ncatice = ncatice
        # ice thickness category boundaries copied from ocean.output
        if hiceb is None:
            self.hiceb = np.array( [0.000000000000000E+000,\
                                    0.454016742415552,\
                                    1.12931382308363,\
                                    2.14145898894797,\
                                    3.67059640991554,\
                                   99.0000000000000])
        else:
            self.hiceb = hiceb
        if grid=='orca025':
            self.grdfile='coordinates_ORCA025.nc'
            self.readModelGrid(self.grdfile)
        else:
            print "Grid %s not implemented!" % grid
            sys.exit(0)
        self.initNetCDF(fno)

    def initNetCDF(self,fno,fillValue=0):
        today = datetime.today()
        fp = nc.Dataset(fno,'w')
        setattr(fp,'history',"Created by <petteri.uotila@fmi.fi> on %s by %s." % \
                             (today.strftime("%Y-%m-%d"),sys.argv[0]))
        fin = nc.Dataset(self.grdfile)
        fp.createDimension('ncatice',self.ncatice)
        fp.createDimension('y',self.gx)
        fp.createDimension('x',self.gy)
        fp.createDimension('time',None) # unlimited time dimension
        for v_name, varin in fin.variables.iteritems():
            if v_name in ['nav_lat','nav_lon']:
                outVar = fp.createVariable(v_name,varin.dtype,varin.dimensions)
                if v_name=='nav_lat':
                    outVar[:] = self.grdlat
                else: # nav_lon
                    outVar[:] = self.grdlon
                for k in varin.ncattrs():
                    setattr(outVar,k,getattr(varin,k))
        fin.close()
        outVar = fp.createVariable('time','i',('time',))
        outVar.calendar = 'gregorian'
        outVar.standard_name = 'time'
        outVar = fp.createVariable('hiceb','f',('ncatice',))
        outVar[:] = self.hiceb[1:]
        outVar.units = 'm'
        outVar.long_name = 'ice thickness category upper boundaries'
        outVar = fp.createVariable('sitd','f',('time','ncatice','y','x'),fill_value=fillValue)
        outVar.units = " "
        outVar.long_name = 'EM ice thickness count per category'
        outVar.coordinates = "time ncatice nav_lon nav_lat"
        outVar.missing_value = fillValue
        fp.sync()
        self.fp = fp

    def sampleEMThickness(self,emo,lastFile=False,yoffset=0):
        emts = np.array(emo.data)
        time = self.fp.variables['time']
        sitd = self.fp.variables['sitd']
        FillValue = sitd._FillValue
        it = time.shape[0]-1
        if it>=0:
            date = self.prevdate
            cnts = sitd[-1]
        else: # it=-1
            it = 0
            date = datetime(emo.dates[0].year + yoffset,\
                            emo.dates[0].month,emo.dates[0].day)
            time.units = "days since %04d-%02d-%02d" % \
                         (date.year,date.month,date.day)
            cnts = np.zeros((self.ncatice,self.gx,self.gy),dtype='i')
        self.cdftime = utime(time.units,calendar='standard')
        prevdate = date
        for i, emt in enumerate(emts):
            if emt<0.: continue
            # monthly temporal resolution
            date = datetime(emo.dates[i].year+yoffset,\
                            emo.dates[i].month,emo.dates[i].day)
            if date.month!=prevdate.month:
                # store values for previous time step
                time[it] = self.cdftime.date2num(prevdate)
                sitd[it] = cnts
                self.fp.sync()
                print "Stored timestep=%d, max(cnt)=%d" % (it,cnts.max())
                # new time step
                it += 1
                cnts = np.zeros((self.ncatice,self.gx,self.gy),dtype='i')
            if i%10000==0:
                print "Processing timestep=%d %s, i=%d" % \
                      (it,date.strftime("%Y-%m-%d"),i)
            icat = np.where(emt<self.hiceb)[0][0]
            cnts[icat-1,emo.x[i],emo.y[i]] += 1
            prevdate = date
        # store values if the last file
        #if lastFile:
        time[it] = self.cdftime.date2num(date)
        sitd[it] = cnts
        self.fp.sync()
        print "Stored timestep=%d, max(cnt)=%d" % (it,cnts.max())
        # store the last date in the input file
        self.prevdate = date

if __name__ == "__main__":
    sit = obsIceThickDistr('antload_1m_sitd.nc')
    fns = sorted(glob.glob('mittaus*.mat.cpickle.gz'))
    #fns = ['mittaus13.mat.cpickle.gz','mittaus14.mat.cpickle.gz']
    lastFile = False
    for fn in fns:
        if fn==fns[-1]:
            lastFile = True
        if fn in ['mittaus14.mat.cpickle.gz']:
            yoffset = 1 # timestamp has a wrong year (2013 not 2014)
        else:
            yoffset = 0
        print "Reading %s, lastFile=%s and yoffset=%d" % (fn,lastFile,yoffset)
        obj = load_zipped_pickle(fn)
        sit.sampleEMThickness(obj,lastFile,yoffset=yoffset)
    sit.fp.close()
    print "Finnished!"
