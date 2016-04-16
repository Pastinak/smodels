#!/usr/bin/env python

"""
.. module:: testLheDecomposition
   :synopsis: Tests the lheReader and the LHE decomposition
              Depends also on lheDecomposer.

.. moduleauthor:: Wolfgang Waltenberger <wolfgang.waltenberger@gmail.com>
.. moduleauthor:: Andre Lessa <lessa.a.p@gmail.com>

"""

import sys
sys.path.insert(0,"../")
from smodels.theory import decomposer
from smodels.tools.physicsUnits import GeV, fb
from smodels.theory.element import createElementFromStr
from smodels.particleDefinitions import useParticlesNameDict
import unittest



class LheDecompositionTest(unittest.TestCase):
    def testDecomposition(self):
        """ test the LheReader """

        filename = "../inputFiles/lhe/simplyGluino.lhe" 
        toplist = decomposer.decompose(filename)
        self.assertEqual(len(toplist),1)
        self.assertEqual(len(toplist.getElements()),3)
        el0 = createElementFromStr('[[[u,u*]],[[u,u*]]]')
        el1 = createElementFromStr('[[[u,u*]],[[d,d*]]]')        
        el2 = createElementFromStr('[[[d,d*]],[[d,d*]]]')
        els = toplist.getElements()
        
        self.assertEqual(el0, els[0])
        self.assertEqual(el1, els[1])
        self.assertEqual(el2, els[2])
        for el in els:
            print el.weight
            self.assertEqual(el.getOddMasses(), [[675.*GeV,200.*GeV],[675.*GeV,200.*GeV]])

if __name__ == "__main__":
    unittest.main()
