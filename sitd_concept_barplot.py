#!/usr/bin/env python
# a stacked bar plot with errorbars
import numpy as np
import matplotlib.pyplot as plt


N = 5
IceThickness = (0.2, 0.9, 1.5, 2.8, 4.4)
SnowThickness = (0.05, 0.2, 0.3, 0.35, 0.5)
IceSnowThickness = np.array(IceThickness) + np.array(SnowThickness)
ind = np.arange(N)    # the x locations for the groups
width = 0.9          # the width of the bars: can also be len(x) sequence

fig = plt.figure(figsize=(10,5))
ax = fig.add_subplot(1,2,1)
p1 = ax.bar(ind, IceThickness, width, color='darkgrey',linewidth=2)
p2 = ax.bar(ind, SnowThickness, width, color='snow',
                 bottom=IceThickness,linewidth=2)

ax.set_ylabel('Mean Thickness [m]')
ax.set_title('LIM ice thickness categories')
ax.set_xticks(ind + width/2.)
ax.set_xticklabels(('C1', 'C2', 'C3', 'C4', 'C5'))
ax.set_yticks(np.arange(0, 7, 1))
ax.legend((p1[0], p2[0]), ('Ice', 'Snow'))

ax = fig.add_subplot(1,2,2)
p3 = plt.bar(ind, IceSnowThickness, width, color='lightgrey',linewidth=2)
ax.set_title('EM snow+ice thickness categories')
ax.set_xticks(ind + width/2.)
ax.set_xticklabels(('C1', 'C2', 'C3', 'C4', 'C5'))
ax.set_yticks(np.arange(0, 7, 1))
ax.legend((p3[0],), ('Ice+Snow',))
#plt.show()
plt.savefig('lim_sitd_concept.png')

