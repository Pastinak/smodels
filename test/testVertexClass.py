#!/usr/bin/env python

"""
.. module:: testVertexClass
   :synopsis: Tests the theory.particle.Vertex class

.. moduleauthor:: Andre Lessa <lessa.a.p@gmail.com>

"""
import sys
sys.path.insert(0,"../")
import unittest
from smodels.theory.particle import Particle
from smodels.theory.vertex import Vertex, createVertexFromStr
from smodels.tools.physicsUnits import GeV


class VertexTest(unittest.TestCase):        
    def testVertex(self):
        
        p1 = Particle(mass=100.*GeV, zParity=-1)
        p3 = Particle( _pid=1, mass=110.*GeV, zParity=-1)
        p4 = Particle(mass = 110.*GeV, zParity = -1)
        
        sq1 = Particle(name='squark1', mass = 110.*GeV, zParity = -1)
        sq2 = Particle(name='squark1', mass = 100.*GeV, zParity = -1)
        u = Particle(name='u', zParity = 1)
        d = Particle(name='d',mass = 0.01*GeV, zParity = 1)
        
        v1 = Vertex(inParticle=p1, outParticles=[sq1,u,d])
        v2 = Vertex(inParticle=p1, outParticles=[sq1,d])
        v3 = Vertex(inParticle=p1, outParticles=[sq2,d])
        v5 = Vertex(inParticle=p3, outParticles=[sq1,u,d])
        v5b = Vertex(inParticle=p4, outParticles=[sq1,u,d])
        self.assertEqual( str(v1) == '[d,u]', True)
        self.assertEqual( v1.stringRep().replace(' ','') == "-->squark1+[d,u]", True)
        self.assertEqual(v1 > v2, True)  #Larger by number of outgoing particles
        self.assertEqual(v2 > v3, True)  #Larger by mass of sq1
        self.assertEqual(v5b == v5, True)  #All common properties are equal
        
    def testVertexStr(self):
        
        ep = Particle(name='e+',mass = 0.0005*GeV, zParity = 1)
        L = Particle(name='L', zParity = 1)
        mum = Particle(name='mu-', eCharge = -1, mass = 0.106*GeV, zParity = 1)
        inP = Particle(zParity = -1)
        outP = Particle(zParity = -1)
        vstr = createVertexFromStr('[e+,L,mu-]')
        v = Vertex(inParticle=inP, outParticles=[ep,mum,L,outP])
        self.assertEqual(v == vstr, True)  #Check that vertices match
        
if __name__ == "__main__":
    unittest.main()
