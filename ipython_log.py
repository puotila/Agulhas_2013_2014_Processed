# IPython log file

get_ipython().magic(u'logon')
get_ipython().magic(u'logstart')
import netCDF4 as nc
fn = 'antload_1m_sitd.nc'
fp = nc.Dataset(fn)
fp.variables.keys()
sitd = np.ma.array(fp.variables['sitd'][:])
hiceb = np.array(fp.variables['hiceb'][:])
sitd.shape
sitd[2].max()
np.where(sitd[2]==sitd[2].max())
sitd[2,:,116,1126]
hist(sitd[2,:,116,1126])
hist(sitd[2,:,116,1126])
hist(hicb,sitd[2,:,116,1126])
hist(hiceb,sitd[2,:,116,1126])
hiceb.shape
hiceb,sitd[2,:,116,1126].shape
sitd[2,:,116,1126].shape
help(hist)
hist(hiceb,sitd[2,:,116,1126])
hiceb
hist(hiceb[:-1],sitd[2,:-1,116,1126])
hiceb[:-1]
hist(4,sitd[2,:-1,116,1126])
hist(sitd[2,:-1,116,1126])
hist(3,sitd[2,:-1,116,1126])
hist(4,sitd[2,:-1,116,1126])
sitd[2,:-1,116,1126]
sitd[2,:,116,1126]
np.array(sitd[2,:,116,1126])
sitd[2,:,116,1126]
np.array(sitd[2,:,116,1126])
help(bar)
bar(4,sitd[2,:-1,116,1126])
help(bar)
help(hist)
out = hist(4,sitd[2,:-1,116,1126])
out = hist(sitd[2,:-1,116,1126])
help(hist)
out = hist(sitd[2,:-1,116,1126],4)
out = hist(sitd[2,:-1,116,1126],hiceb)
out = hist(sitd[2,:-1,116,1126],hiceb[:-1])
help(bar)
plot(sitd[2,:,116,1126])
plot(sitd[2,:,116,1126],step)
plot(sitd[2,:,116,1126],step)
help(plot)
plot(hiceb,sitd[2,:,116,1126],drawstyle='steps-post')
plot(hiceb,sitd[2,:,116,1126],drawstyle='steps-pre')
plot(hiceb,sitd[2,:,116,1126],drawstyle='steps-post')
hiceb
plot(hiceb,sitd[2,:,116,1126],drawstyle='steps-pre')
plot([0]+hiceb,sitd[2,0,116,1126]+sitd[2,:,116,1126],drawstyle='steps-pre')
np.hstack([0],hiceb)
np.hstack(([0],hiceb))
plot(np.hstack(([0]+hiceb)),sitd[2,0,116,1126]+sitd[2,:,116,1126],drawstyle='steps-pre')
np.hstack((sitd[2,0,116,1126],sitd[2,:,116,1126]))
np.ma.hstack((sitd[2,0,116,1126],sitd[2,:,116,1126]))
plot(np.hstack(([0]+hiceb)),np.ma.hstack((sitd[2,0,116,1126],sitd[2,:,116,1126])),drawstyle='steps-pre')
np.hstack(([0]+hiceb)),np.ma.hstack((sitd[2,0,116,1126],sitd[2,:,116,1126])
)
plot(np.hstack(([0],hiceb)),np.ma.hstack((sitd[2,0,116,1126],sitd[2,:,116,1126])),drawstyle='steps-pre')
sitd[2,:,116,1126].sum()
plot(np.hstack(([0],hiceb)),np.ma.hstack((sitd[2,0,116,1126],sitd[2,:,116,1126]))/sitd[2,:,116,1126].sum(),drawstyle='steps-pre')
plot(np.hstack(([0],hiceb)),np.ma.hstack((sitd[2,0,116,1126],sitd[2,:,116,1126]))/sitd[2,:,116,1126].sum(),drawstyle='steps-pre',lw=2)
fm = '/lustre/tmp/uotilap/NO01/output/nemo/422/NO02_1m_20140101_20140131_icemod.nc'
fp2 = nc.Dataset(fm)
67*5
35767*5
357-67*5
22+67*10
22+67*9
22+67*8
22+67*10
22+67*12
get_ipython().magic(u'who')
