#!/usr/bin/env python
"""
Simple plotting of one grid cell ice thickness distributions, observed and
modelled. Might evolve to something bigger.
"""

import sys
import numpy as np
import netCDF4 as nc
import matplotlib.pylab as plt
from matplotlib import colors
from scipy.stats import ks_2samp

class LIM3SITD(object):
    def __init__(self,fn,tidx=0):
        """ Assume monthly files with one time record
        """
        fp = nc.Dataset(fn)
        siconcat = np.ma.array(fp.variables['siconcat'][tidx])
        sithicat = np.ma.array(fp.variables['sithicat'][tidx])
        snthicat = np.ma.array(fp.variables['snthicat'][tidx])
        sinthicat = sithicat + snthicat # ice + snow thickness
        # used category thickness as sithicat + snthicat as EM sees the ice
        # adjust category bounds back so that they correspod to ice thickness
        # category bounds
        siconcatEM = np.ma.zeros(siconcat.shape)
        # first category
        siconcatEM[0] = siconcat[0]*sithicat[0]/sinthicat[0]
        # 2..N-1 categories
        siconcatEM[1:-1] = np.ma.array([siconcat[i]*\
                                       (snthicat[i-1]+sithicat[i])/sinthicat[i] \
                                        for i in range(1,len(siconcat)-1)])
        # Nth category
        siconcatEM[-1] = siconcat[-1]*(snthicat[-2]+snthicat[-1]+sithicat[-1])/sinthicat[-1]
        # normalise sitd so that its sum per grid cell is one
        # effectively convert volume to thickness
        self.siconcat = np.ma.array([siconcatEM[i,:,:]/np.sum(siconcatEM,axis=0) \
                                     for i in range(siconcatEM.shape[0])])
        self.lat = np.array(fp.variables['nav_lat'])
        self.lon = np.array(fp.variables['nav_lon'])
        fp.close()

class EMSITD(object):
    def __init__(self,fn,tidx=0):
        fp = nc.Dataset(fn)
        sitd = np.ma.sum(fp.variables['sitd'][tidx,:,:,:],axis=0)
        # number of processed 100m EM observations per grid cell
        self.cnt = np.ma.sum(sitd,axis=0)
        # normalise sitd so that its sum per grid cell is one
        self.sitd = np.ma.array([sitd[i,:,:]/np.sum(sitd,axis=0) \
                                 for i in range(sitd.shape[0])])
        # upper boundaries of ice thicness category limits
        hiceb = np.ma.array(fp.variables['hiceb'])
        # add lower boundary (0) and change upper boudary (5)
        self.hicats = np.hstack(([0],hiceb[:-1],[5]))
        # mean of ice categories thicknesses
        self.hicatmean = (self.hicats[1:]+self.hicats[:-1])/2
        self.lat = np.array(fp.variables['nav_lat'])
        self.lon = np.array(fp.variables['nav_lon'])
        fp.close()

class PlotObsMods(object):
    def __init__(self,obs,mod):
        self.obs = obs
        self.mod = mod

    def plotSITD(self,iy,ix,title='Jan 2014'):
        obs = self.obs
        mod = self.mod
        plat = obs.lat[iy,ix]
        plon = obs.lon[iy,ix]
        nobs = obs.cnt[iy,ix]
        hiobs = obs.sitd[:,iy,ix]
        himod = mod.siconcat[:,iy,ix]
        # mean values (skip the last category):
        mhiobs = np.ma.sum(obs.hicatmean[:-1]*hiobs[:-1])
        mhimod = np.ma.sum(obs.hicatmean[:-1]*himod[:-1])
        fig = plt.figure()
        ax = fig.add_subplot(1,1,1)
        x = np.ma.hstack((np.ma.hstack(([l for pair in zip(obs.hicats[:-1],obs.hicats[:-1]) for l in pair])),[5.]))
        yobs = np.ma.hstack(([0.],[l for pair in zip(hiobs,hiobs) for l in pair]))
        ymod = np.ma.hstack(([0.],[l for pair in zip(himod,himod) for l in pair]))
        lnes = ax.plot(x,yobs,x,ymod,lw=2)
        ax.set_xticks(obs.hicats)
        ax.set_xlim(-0.1,5.1)
        ax.set_xlabel('ice thickness [m]')
        ax.set_ylabel('ice concentration [0-1]')
        ax.legend(lnes,("obs, <%4.2f m>" % mhiobs,"model, <%4.2f m>" % mhimod))
        ax.set_title("%s, %5.1f E,%4.1f N, N$_{obs}$=%d" % (title,plon,plat,nobs))
        plt.savefig('sitd_%s_y%d_x%d.png' % (title.replace(' ','_'),iy,ix))

    def mapPlot(self,fld,title='p-values Jan 2014'):
        from mpl_toolkits.basemap import Basemap
        m = Basemap(width=600000,height=600000,\
                    projection='laea',resolution='h',\
                    lat_ts=-69,lat_0=-69,lon_0=-6.)
        x,y = m(self.obs.lon,self.obs.lat)
        fig = plt.figure()
        ax = fig.add_subplot(1,1,1)
        bounds = np.array([0, 0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99, 1])
        norm = colors.BoundaryNorm(boundaries=bounds, ncolors=256)
        m.pcolormesh(x,y,fld,norm=norm,cmap=plt.get_cmap('RdYlGn'))
        m.drawcoastlines()
        m.drawmeridians(np.arange(-30,14,4),labels=[0,0,0,1])
        m.drawparallels(np.arange(-70,-50,2),labels=[1,0,0,0])
        m.colorbar()
        plt.savefig('map_%s.png' % title.replace(' ','_'))

if __name__ == "__main__":
    fon = 'antload_1m_sitd.nc'
    imonths = [1,2] # Jan and early Feb 2014
    emdata = EMSITD(fon,tidx=imonths)
    fmn = 'NO02_1m_20140101_20140131_icemod.nc'
    #fmn = 'NO02_1m_20140201_20140228_icemod.nc'
    limdata = LIM3SITD(fmn)
    # calculate KS stats per grid cell
    pvals = np.ma.zeros(emdata.lat.shape)
    pvals.mask = True
    for iy in range(emdata.lat.shape[0]):
        for ix in range(emdata.lat.shape[1]):
            if emdata.sitd[:-1,iy,ix].mask.any(): continue
            if limdata.siconcat[:-1,iy,ix].mask.any(): continue
            tval, pvals[iy,ix] = ks_2samp(emdata.sitd[:-1,iy,ix],\
                                          limdata.siconcat[:-1,iy,ix])
    # plotting
    ompl = PlotObsMods(emdata,limdata)
    # sitd plots
    iy, ix = 108, 1123 # (where pval is high)
    ompl.plotSITD(iy,ix)
    iy, ix = 94, 1118 # (where pval is low)
    ompl.plotSITD(iy,ix)
    iy, ix = 100, 1143 # (where pval is around 0.5)
    ompl.plotSITD(iy,ix)
    print "Finnished!"
