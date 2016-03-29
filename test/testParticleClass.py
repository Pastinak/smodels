#!/usr/bin/env python

"""
.. module:: testParticleClass
   :synopsis: Tests the theory.particle.Particle class

.. moduleauthor:: Andre Lessa <lessa.a.p@gmail.com>

"""
import sys
sys.path.insert(0,"../")
import unittest

class ParticleTest(unittest.TestCase):
    def testParticle(self):        
        from smodels.theory.particle import Particle
        from smodels.tools.physicsUnits import GeV
                
        p1 = Particle(name='gluino', pid=1000021, mass=100.*GeV, spin=1/2, 
                      eCharge=0, qColor = 8, zParity=-1)

        p2 = Particle(name='gluino', pid=1000021, spin=1/2, 
                      eCharge=0, qColor = 8, zParity=-1)
        p3 = Particle(name='gluino', pid=1000021, mass=110.*GeV, spin=1/2, 
                      eCharge=0, qColor = 8, zParity=-1)
        p4 = Particle(name='squark')          
        p5 = Particle(name='gluino')
        
        p1c = p1.copy()
                
        self.assertEqual( str(p1), 'gluino')
        self.assertEqual( p1 == p2, True)
        self.assertEqual( p1 == p3, False)        
        self.assertEqual( p5 == p2 == p1, True)
        self.assertEqual( p1c == p1, True)
        self.assertEqual( p1c == p3, False)

if __name__ == "__main__":
    unittest.main()
