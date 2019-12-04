#!/usr/bin/env python3

"""
.. module:: pyhfInterface
   :synopsis: Code that delegates the computation of limits and likelihoods to
              pyhf.

.. moduleauthor:: Gael Alguero <gaelalguero@gmail.com>
.. moduleauthor:: Wolfgang Waltenberger <wolfgang.waltenberger@gmail.com>

"""

from __future__ import print_function
import json
import jsonpatch
import pyhf
from scipy import optimize

def getLogger():
    """
    Configure the logging facility. Maybe adapted to fit into
    your framework.
    """
    
    import logging
    
    logger = logging.getLogger("SL")
    formatter = logging.Formatter('%(module)s - %(levelname)s: %(message)s')
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    ch.setLevel(logging.DEBUG)
    logger.addHandler(ch)
    return logger

logger=getLogger()

class PyhfUpperLimitComputer:
    def __init__ ( self, data, cl):
        self.data = data
        self.cls = cl
        self.regions = readRegions(self.data)
        self.patches = patchMaker(self.data)
        self.jsonInput = jsonMaker()
        
    def patchMaker(data):
        nsignals = self.data.nignals
        patches = []
        for reg in self.regions:
            nSR = len(regFile)
            patch_dic = {}
            patch_dic["op"]    = "replace"
            patch_dic["path"]  = "/channels/0/samples/0/data"
            patch_dic["value"] = nsignals[:nSR-1]
            nsignals = nsignals[nSR:]
            patches.append([patch_dic])
        return patches
    
    def readRegions(self):
            
    
    def jsonMaker(self):
        jsonInputs = []
        for reg, patch in zip(self.regions,self.patches):
            # Open BckOnly.json
            jsonInputs.append(jsonpatch.apply_patch(BckOnly, patch))
        # Concatenate (jsonInputs) -> jsonInput
        jsonInput = {}
        jsonInput["channels"] = []
        for json in jsonInputs:
            dumpJson = json.dump(json)
                for channel in dumpJson["channels"]:
            jsonInput["channels"].append(channel)
        jsonInput["observations"] = []
        for json in jsonInputs:
            dumpJson = json.dump(json)
            for observation in dumpJson["observations"]:
                jsonInput["observations"].append(observation)
        jsonInput["measurements"] = jsonInputs[0]["measurements"]
        jsonInput["version"] = jsonInputs[0]["version"]
        # These two last are the same
        return json.load(jsonInput)

    def ulSigma (self, expected=False):
        jsonInput = ...
        def root_func(mu):
            # Opening main workspace file of region A
            wspec = self.jsonInput
            w = pyhf.Workspace(wspec)
            # Same modifiers_settings as those use when running the 'pyhf cls' command line
            msettings = {'normsys': {'interpcode': 'code4'}, 'histosys': {'interpcode': 'code4p'}}
            p = w.model(measurement_name=None, patches=[], modifiers_settings=msettings)
            test_poi = mu
            result = pyhf.utils.hypotest(test_poi, w.data(p), p, qtilde=True, return_expected_set = True)
            if expected:
                CLs = result[1].tolist()[2][0]
            else:
                CLs = result[0].tolist()[0]
            return 1.0 - cl - CLs
        # Finding the root (Brent bracketing part)
        lo_mu = 1.0
        hi_mu = 1.0
        while root_func(hi_mu) < 0.0:
            hi_mu *= 10
        while root_func(lo_mu) > 0.0:
            lo_mu /=10
        ul = optimize.brentq(root_func, lo_mu, hi_mu, rtol=1e-3, xtol=1e-3)
        return None

if __name__ == "__main__":
    C = [ 18774.2, -2866.97, -5807.3, -4460.52, -2777.25, -1572.97, -846.653, -442.531,
       -2866.97, 496.273, 900.195, 667.591, 403.92, 222.614, 116.779, 59.5958,
       -5807.3, 900.195, 1799.56, 1376.77, 854.448, 482.435, 258.92, 134.975,
       -4460.52, 667.591, 1376.77, 1063.03, 664.527, 377.714, 203.967, 106.926,
       -2777.25, 403.92, 854.448, 664.527, 417.837, 238.76, 129.55, 68.2075,
       -1572.97, 222.614, 482.435, 377.714, 238.76, 137.151, 74.7665, 39.5247,
       -846.653, 116.779, 258.92, 203.967, 129.55, 74.7665, 40.9423, 21.7285,
       -442.531, 59.5958, 134.975, 106.926, 68.2075, 39.5247, 21.7285, 11.5732]
    nsignal = [ x/100. for x in [47,29.4,21.1,14.3,9.4,7.1,4.7,4.3] ]
    m=Data( observed=[1964,877,354,182,82,36,15,11],
              backgrounds=[2006.4,836.4,350.,147.1,62.0,26.2,11.1,4.7],
              covariance= C,
#              third_moment = [ 0.1, 0.02, 0.1, 0.1, 0.003, 0.0001, 0.0002, 0.0005 ],
              third_moment = [ 0. ] * 8,
              nsignal = nsignal,
              name="ATLAS-SUSY-2018-31 model" )
    ulComp = PyhfUpperLimitComputer(cl=.95)
    #uls = ulComp.ulSigma ( Data ( 15,17.5,3.2,0.00454755 ) )
    #print ( "uls=", uls )
    ul_old = 131.828*sum(nsignal) #With respect to the older refernece value one must normalize the xsec
    print ( "old ul=", ul_old )
    ul = ulComp.ulSigma ( m )
    print ( "ul (marginalized)", ul )
    ul = ulComp.ulSigma ( m, marginalize=False )
    print ( "ul (profiled)", ul )
