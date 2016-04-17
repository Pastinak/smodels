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
from smodels.tools.physicsUnits import GeV, fb,pb
from smodels.theory.element import createElementFromStr
from smodels.theory import decomposer
import unittest


class LheDecompositionTest(unittest.TestCase):
    def testSimpleDecomposition(self):
        """ test the Decomposition """
 
        filename = "../inputFiles/lhe/simplyGluino.lhe" 
        toplist = decomposer.decompose(filename)
        self.assertEqual(len(toplist),1)
        self.assertEqual(len(toplist.getElements()),3)
        el0 = createElementFromStr('[[[d,d*]],[[d,d*]]]')
        el1 = createElementFromStr('[[[u,u*]],[[d,d*]]]')
        el2 = createElementFromStr('[[[u,u*]],[[u,u*]]]')
        els = toplist.getElements()
         
        self.assertEqual(el0, els[0])
        self.assertEqual(el1, els[1])
        self.assertEqual(el2, els[2])
        weight = [0.262115*pb*0.3*0.3,0.262115*pb*0.7*0.3*2,0.262115*pb*0.7*0.7]
        for iel,el in enumerate(els):
            self.assertAlmostEqual(el.weight[0].value.asNumber(fb),weight[iel].asNumber(fb),2)
            self.assertEqual(el.getOddMasses(), [[675.*GeV,200.*GeV],[675.*GeV,200.*GeV]])
            
    def testComplexDecomposition(self):
        """ test the Decomposition """
 
        filename = "../inputFiles/lhe/gluino_squarks.lhe" 
        toplist = decomposer.decompose(filename)         
        self.assertEqual(len(toplist),15)
        self.assertEqual(len(toplist.getElements()),225)

        
        el0 = createElementFromStr('[[[u]],[[s,s*]]]')
        el = toplist.topos[2].elementList[-1]
        self.assertEqual(el0, el)
        self.assertEqual(el.getOddMasses(), [[991.299127*GeV,128.961570*GeV],[865.035125*GeV,128.961570*GeV]])
        self.assertAlmostEqual(el.weight[0].value.asNumber(fb),0.1739,3)
            

if __name__ == "__main__":
    unittest.main()
