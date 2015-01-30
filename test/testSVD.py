#!/usr/bin/env python

"""
.. module:: testInterpolation
   :synopsis: Tests the retrieval of the upper limits, including the PCA.
              Will replace the upper limit test

.. moduleauthor:: Wolfgang Waltenberger <wolfgang.waltenberger@gmail.com>

"""
import unittest
from smodels.experiment.sVDTrafo import SVDTrafo
from smodels.tools.physicsUnits import GeV, fb

class SVDTest(unittest.TestCase):
    def testSVD(self):
        data = [ [ [[ 300.*GeV,100.*GeV], [ 300.*GeV,100.*GeV] ], 10.*fb ], 
                 [ [[ 300.*GeV,150.*GeV], [ 300.*GeV,150.*GeV] ], 13.*fb ], 
                 [ [[ 300.*GeV,200.*GeV], [ 300.*GeV,200.*GeV] ], 15.*fb ], 
                 [ [[ 300.*GeV,250.*GeV], [ 300.*GeV,250.*GeV] ], 20.*fb ], 
                 [ [[ 400.*GeV,100.*GeV], [ 400.*GeV,100.*GeV] ], 8.*fb ], 
                 [ [[ 400.*GeV,150.*GeV], [ 400.*GeV,150.*GeV] ], 10.*fb ], 
                 [ [[ 400.*GeV,200.*GeV], [ 400.*GeV,200.*GeV] ], 12.*fb ], 
                 [ [[ 400.*GeV,250.*GeV], [ 400.*GeV,250.*GeV] ], 15.*fb ], 
                 [ [[ 400.*GeV,300.*GeV], [ 400.*GeV,300.*GeV] ], 17.*fb ], 
                 [ [[ 400.*GeV,350.*GeV], [ 400.*GeV,350.*GeV] ], 19.*fb ], 
                 ]
        trafo=SVDTrafo ( data )
        print "upper limit for 300,100=", trafo.getUpperLimit ( [[ 300.*GeV,100.*GeV], [ 300.*GeV,100.*GeV] ] )
        print "upper limit for 400,300=", trafo.getUpperLimit ( [[ 400.*GeV,300.*GeV], [ 400.*GeV,300.*GeV] ] )
        print "upper limit for 300,125=", trafo.getUpperLimit ( [[ 300.*GeV,125.*GeV], [ 300.*GeV,125.*GeV] ] )
        print "upper limit for 300,120=", trafo.getUpperLimit ( [[ 300.*GeV,120.*GeV], [ 300.*GeV,120.*GeV] ] )
        print "upper limit for 300,120,300,125=", trafo.getUpperLimit ( [[ 300.*GeV,120.*GeV], [ 300.*GeV,125.*GeV] ] )

if __name__ == "__main__":
    unittest.main()
