#!/usr/bin/env python

"""
.. module:: testParticleClass
   :synopsis: Tests the theory.particle.Particle class

.. moduleauthor:: Andre Lessa <lessa.a.p@gmail.com>

"""
import sys
sys.path.insert(0,"../")
import unittest
from smodels.theory.particle import Particle
from smodels.theory.vertex import Vertex
from smodels.tools.physicsUnits import GeV


g = Particle(name='gluino', _pid=1000021, mass=100.*GeV, spin=1/2, 
              eCharge=0, qColor = 8, zParity=-1)

p2 = Particle(name='gluino', _pid=1000021, spin=1/2, 
              eCharge=0, qColor = 8, zParity=-1)
p3 = Particle(name='gluino', _pid=1, mass=110.*GeV, spin=1/2, 
              eCharge=0, qColor = 8, zParity=-1)
sq = Particle(name='squark', zParity = -1)          
p5 = Particle(name='gluino', zParity = -1)
u = Particle(name='u', zParity = 1)
d = Particle(name='d', zParity = 1)

p1c = g.copy()

class ParticleTest(unittest.TestCase):
    def testParticle(self):                
        self.assertEqual( str(g), 'gluino')
        self.assertEqual( g == p2, True)
        self.assertEqual( g == p3, False)        
        self.assertEqual( p5 == p2 == g, True)
        self.assertEqual( p1c == g, True)
        self.assertEqual( p1c == p3, False)
        self.assertEqual( sq == p5, False)
        
    def testVertex(self):
        
        v1 = Vertex(inParticle=g, outParticles=[sq,u,d])

        self.assertEqual( str(v1) == str(sorted(['d','u'])), True)
        self.assertEqual( v1.stringRep().replace(' ','') == "gluino-->squark+['d','u']", True)
        
if __name__ == "__main__":
    unittest.main()
