#!/usr/bin/env python

"""
.. module:: testSlhaDecomposition
   :synopsis: Checks slha decomposition, alongside with compression
    
.. moduleauthor:: Wolfgang Waltenberger <wolfgang.waltenberger@gmail.com>
    
"""

import sys
sys.path.insert(0,"../")
from smodels.theory import decomposer
from smodels.tools.physicsUnits import GeV, fb
from smodels.theory.element import createElementFromStr
import unittest
import logging
#import logging.config

class SlhaDecompositionTest(unittest.TestCase):
    logger = logging.getLogger(__name__)

    def testSimple(self):
        self.logger.info ( "test a simple decomposition, no compression" )
        """ test the decomposition with no compression """
        slhafile="../inputFiles/slha/simplyGluino.slha"
        topos = decomposer.decompose( slhafile, .1*fb, False, False, 5.*GeV )
        self.assertEqual( len(topos), 1 )
        #print len(topos),"topologies."
        topo=topos[0]
        #print topo
        ellist=topo.elementList
        self.assertEqual( len(ellist), 3 )
        self.assertEqual( str(ellist[0]), "[[[u,u*]],[[u,u*]]]" )
        elStr = createElementFromStr("[[[jet,jet]],[[jet,jet]]]")
        for el in ellist:
            self.assertEqual(el,elStr)
             
        gluinoxsec = 572.1689*fb
        br = 0.5
        self.assertAlmostEqual(ellist[0].weight[0].value.asNumber(fb),
                               (gluinoxsec*br*br).asNumber(fb),3)
        self.assertAlmostEqual(ellist[1].weight[0].value.asNumber(fb),
                               2*(gluinoxsec*br*br).asNumber(fb),3)
        self.assertAlmostEqual(ellist[2].weight[0].value.asNumber(fb),
                               (gluinoxsec*br*br).asNumber(fb),3)
        
    def testComplex(self):
        self.logger.info ( "test a complex decomposition, no compression" )
        """ test the decomposition with no compression """
        slhafile="../inputFiles/slha/lightEWinos.slha"
        topos = decomposer.decompose( slhafile, .5*fb, False, False, 5.*GeV )
        self.assertEqual(len(topos), 17)
        self.assertEqual(len(topos.getElements()), 364)
        #print len(topos),"topologies."
        el=topos[0].elementList[0]
        self.assertEqual(len(topos[0].elementList), 1)
        self.assertEqual(len(topos[-1].elementList), 64)
        elStr = createElementFromStr("[[],[[Z]]]")
        self.assertEqual(el, elStr)
        el = topos.getElements()[-1]
        elStr = createElementFromStr("[[[b+,t+],[c*,s]],[[g],[W+],[c*,s]]]")
        self.assertEqual(el, elStr)
        w = 2.*0.86*fb
        self.assertAlmostEqual(el.weight[0].value.asNumber(fb), w.asNumber(fb), 2)
        

if __name__ == "__main__":
    unittest.main()
