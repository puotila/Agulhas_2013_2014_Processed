#!/usr/bin/env python
"""
Simple plotting of one grid cell ice thickness distributions, observed and
modelled. Might evolve to something bigger.
"""

import sys
import numpy as np
import rpy
import netCDF4 as nc
import matplotlib.pylab as plt
from matplotlib import colors
from scipy.stats import ks_2samp

from plotEMandLIMDistros import LIM3SITD, EMSITD, PlotObsMods

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
    # pvals on map
    ompl.mapPlot(pvals,title='scipy.ks2amp p-values Jan 2014')
    # calculate rpy KS stats per grid cell
    pvals = np.ma.zeros(emdata.lat.shape)
    pvals.mask = True
    for iy in range(emdata.lat.shape[0]):
        for ix in range(emdata.lat.shape[1]):
            if emdata.sitd[:-1,iy,ix].mask.any(): continue
            if limdata.siconcat[:-1,iy,ix].mask.any(): continue
            out = rpy.r.ks_test(emdata.sitd[:-1,iy,ix],\
                                limdata.siconcat[:-1,iy,ix])
            pvals[iy,ix] = out['p.value']
    # plotting
    ompl = PlotObsMods(emdata,limdata)
    # pvals on map
    ompl.mapPlot(pvals,title='rpy.r.ks_test p-values Jan 2014')
    # calculate rpy Mann-Whitney stats per grid cell
    pvals = np.ma.zeros(emdata.lat.shape)
    pvals.mask = True
    for iy in range(emdata.lat.shape[0]):
        for ix in range(emdata.lat.shape[1]):
            if emdata.sitd[:-1,iy,ix].mask.any(): continue
            if limdata.siconcat[:-1,iy,ix].mask.any(): continue
            out = rpy.r.wilcox_test(emdata.sitd[:-1,iy,ix],\
                                    limdata.siconcat[:-1,iy,ix],\
                                    exact=True)
            pvals[iy,ix] = out['p.value']
    # plotting
    ompl = PlotObsMods(emdata,limdata)
    # pvals on map
    ompl.mapPlot(pvals,title='rpy.r.wilcox_test p-values Jan 2014')

    print "Finnished!"
