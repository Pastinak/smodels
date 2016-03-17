#!/usr/bin/env python

"""
.. module:: testUpperLimit
   :synopsis: Test smsInterpolation.upperLimit with various inputs

.. moduleauthor:: Ursula Laa <Ursula.Laa@assoc.oeaw.ac.at>

"""
import sys
sys.path.insert(0,"../")
import unittest
from smodels.tools.physicsUnits import GeV, pb
from smodels.installation import installDirectory
from smodels.experiment.database import Database
database=Database ( "./database", verbosity='error' )

class UpperLimitTest(unittest.TestCase):

    def testDirectDecay(self):
        expRes=database.getExpResults ( analysisIDs = [ "ATLAS-SUSY-2013-05" ], 
                    datasetIDs= [ None ] , txnames= [ "T2bb" ] )
        ul = expRes[0].getUpperLimitFor (txname= "T2bb",  
                    mass=[[400*GeV,100*GeV],[400*GeV,100*GeV]] ).asNumber ( pb )
        self.assertAlmostEquals ( ul, 0.0608693 )

    def testOutofBounds(self):
        expRes=database.getExpResults ( analysisIDs = [ "ATLAS-SUSY-2013-05" ], 
                datasetIDs= [ None ] , txnames= [ "T6bbWW" ] )
        ul = expRes[0].getUpperLimitFor (txname= "T6bbWW",  
                mass=[[400*GeV,250*GeV,100*GeV],[400*GeV,250*GeV,100*GeV]] )
        self.assertTrue ( ul == None )

    def testCascadeDecay(self):
        expRes=database.getExpResults ( analysisIDs = [ "ATLAS-SUSY-2013-05" ], 
                    datasetIDs= [ None ] , txnames= [ "T6bbWW" ] )
        ul = expRes[0].getUpperLimitFor (txname= "T6bbWW",  
         mass=[[150*GeV,140*GeV,135*GeV],[150*GeV,140*GeV,135*GeV]] ).asNumber ( pb )
        self.assertAlmostEquals ( ul, 324.682 )

if __name__ == "__main__":
    unittest.main()

