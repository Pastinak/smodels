#!/usr/bin/python3

from __future__ import print_function
import sys, os, time
sys.path.insert(0,"../")
from smodels.experiment.databaseObj import Database
from smodels.theory.theoryPrediction import theoryPredictionsFor
from smodels.experiment.exceptions import SModelSExperimentError
from smodels.tools.smodelsLogging import setLogLevel
from smodels.tools.colors import colors
from smodels.tools.physicsUnits import pb, fb, GeV
from smodels.tools.likelihoods import LikelihoodComputer
from smodels.tools.statistics import UpperLimitComputer
from smodels.theory import slhaDecomposer

LikelihoodComputer.deltas_default = 1e-12
LikelihoodComputer.debug_mode = True
UpperLimitComputer.debug_mode = True


colors.on = True
setLogLevel ( "debug" )
setLogLevel ( "info" )

smstoplist = smstoplist = slhaDecomposer.decompose( "T2tt_528_324_528_324.slha" )
print ( "smstoplist=",len(smstoplist ) )
dir = "covdb/"

if len ( sys.argv) > 1:
    dir = sys.argv[1]

d=Database( dir, discard_zeroes = True )
print(d)

massvec = [[400.*GeV,75*GeV], [400*GeV,75*GeV]]

for e in d.getExpResults():
    print ( e.globalInfo.id )
    #for ds in e.datasets:
    #    print ( ds.dataInfo.dataId )
    predictions = theoryPredictionsFor ( e, smstoplist, useBestDataset=False, 
                                         combinedResults=True )
    for pred in predictions[-1:]:
        print ( pred.describe() )

