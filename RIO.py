"""
Module for POLARIS Polar Operational Limit Assessment Risk Indexing System
which is part of the Polar Code by IACS.
Risk Values are in the table and their sea-ice concentration weighted average
provides Risk Index Outcome (RIO).
"""

__author__ = "<petteri.uotila@fmi.fi>"
__date__= "09082016"
__version__ = 0.1

import numpy as np

class RIO(object):
    def __init__(self):
        self.category = ['A']*5+['B']*2+['C']*5
        self.iceClass = ['PC1','PC2','PC3','PC4',\
                         'PC5','PC6','PC7',\
                         'IA Super','IA','IB','IC',\
                         'Not ice strengthened']
        self.iceType = ['Ice Free','New Ice','Grey Ice',\
                        'Grey White Ice',
                        'Thin First Year Ice, 1st Stage',\
                        'Thin First Year Ice, 2nd Stage',\
                        'Medium First Year Ice',\
                        'Medium First Year Ice, 2nd',\
                        'Thick First Year Ice',\
                        'Second Year Ice',\
                        'Light Multi Year Ice',\
                        'Heavy Multi Year Ice']
        # maximum thickness for each icetype
        self.hi_max = np.array([0.10,0.15,0.30,0.50,0.70,0.95,1.20,2.00,2.50,3.00,99.0])
        # Risk Values
        self.RVs = [[ 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, 1, 1],\
                    [ 3, 3, 3, 3, 2, 2, 2, 2, 2, 1, 1, 0],\
                    [ 3, 3, 3, 3, 2, 2, 2, 2, 2, 1, 0,-1],\
                    [ 3, 3, 3, 3, 2, 2, 2, 2, 1, 0,-1,-2],\
                    [ 3, 3, 3, 3, 2, 2, 2, 1, 0,-1,-2,-2],\
                    [ 3, 2, 2, 2, 2, 1, 1, 0,-1,-2,-3,-3],\
                    [ 3, 2, 2, 2, 2, 1, 0,-1,-2,-3,-3,-3],\
                    [ 3, 2, 2, 2, 2, 1, 0,-1,-2,-3,-4,-4],\
                    [ 3, 2, 2, 2, 1, 0,-1,-2,-3,-4,-4,-4],\
                    [ 3, 2, 2, 1, 0,-1,-2,-3,-3,-4,-5,-5],\
                    [ 3, 2, 1, 0,-1,-2,-2,-3,-4,-4,-5,-6],\
                    [ 3, 1, 0,-1,-2,-2,-3,-3,-4,-5,-6,-6]]

    def getRV(self,iceClass,iceType=None,iceThickness=0.0):
        """ Give ship ice class and ice type or ice thickness,
            return Risk Value from RVs table.
        """
        ic = [i for i,iclass in enumerate(self.iceClass) if iclass==iceClass][0]
        if iceType is None:
            iceType = self.getIceTypefromIceThickness(iceThickness)
        it = [i for i,itype  in enumerate(self.iceType) if itype==iceType][0]
        return self.RVs[ic][it]

    def getIceTypefromIceThickness(self,iceThickness):
        """ Ice thickness in metres.
        """
        it = np.where(self.hi_max>=iceThickness)[0][0] + 1
        return self.iceType[it]

if __name__=="__main__":
    rio = RIO()
    rv  = rio.getRVfromIceType('Not ice strengthened','Ice Free')
