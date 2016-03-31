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
from smodels.tools.physicsUnits import GeV


p1 = Particle(mass=100.*GeV, zParity=-1)
p2 = Particle(_pid=1000021, zParity=-1)
p3 = Particle( _pid=1, mass=110.*GeV, zParity=-1)
p4 = Particle(mass = 110.*GeV, zParity = -1)
p1c = p1.copy()

sq1 = Particle(name='squark1', mass = 110.*GeV, zParity = -1)
sq2 = Particle(name='squark1', mass = 100.*GeV, zParity = -1)
sq3 = Particle(name='squark2', mass = 110.*GeV, zParity = -1)
u = Particle(name='u', zParity = 1)
d = Particle(name='d',mass = 0.01*GeV, zParity = 1)



class ParticleTest(unittest.TestCase):
    def testParticle(self):                
        self.assertEqual( str(p1), '')
        self.assertEqual( str(sq1), 'squark1')
        self.assertEqual( p1 == p2, True) #Only common property for comparison is zParity
        self.assertEqual( p1 > p3, False) #Smaller by mass        
        self.assertEqual( p4 == p3 == p2, True)
        self.assertEqual( p1c == p1, True)
        self.assertEqual( p1c == p3, False) #Differ by mass
        self.assertEqual( sq1 == p4, True) #Only common property for comparison is mass and zParity
        self.assertEqual( sq1 > p1, True)  #Larger by mass
        self.assertEqual( sq1 > sq2, True)  #Larger by mass
        self.assertEqual( sq1 > sq3, False)  #Smaller by name
        self.assertEqual( u > d, True)  #Larger by name
        self.assertEqual( sq1 > d, False)  #Smaller by zParity

        
if __name__ == "__main__":
    unittest.main()
