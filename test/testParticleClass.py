#!/usr/bin/env python

"""
.. module:: testParticleClass
   :synopsis: Tests the theory.particle.Particle class

.. moduleauthor:: Andre Lessa <lessa.a.p@gmail.com>

"""
import sys
sys.path.insert(0,"../")
import unittest
from smodels.theory.particle import Particle, ParticleList, setInternalID
from smodels.tools.physicsUnits import GeV
import pickle

#Load the particle dictionaries
f = open("particleDefinitions.pcl","rb")
modelParticles = pickle.load(f)
particlesDict = dict([[p._name,p] for p in modelParticles])
f.close()


p1 = Particle(mass=100.*GeV, zParity=-1)
p2 = Particle(_pid=1000021, zParity=-1)
p3 = Particle( _pid=1, mass=110.*GeV, zParity=-1)
p4 = Particle(mass = 110.*GeV, zParity = -1)
p1c = p1.copy()
p1d = p1.copy(relevantProp=['zParity']) #Keep only zParity

sq1 = Particle(_name='squark1', mass = 110.*GeV, zParity = -1)
sq2 = Particle(_name='squark1', mass = 100.*GeV, zParity = -1)
sq3 = Particle(_name='squark2', mass = 110.*GeV, zParity = -1)
A = Particle(_name='A', zParity = 1)
B = Particle(_name='B',mass = 0.01*GeV, zParity = 1)
u = particlesDict['u']
d = particlesDict['d']



class ParticleTest(unittest.TestCase):
    def testParticle(self):                
        self.assertEqual( str(p1), '')
        self.assertEqual( str(sq1), 'squark1')
        self.assertEqual( p1 == p2, True) #Only common property for comparison is zParity
        self.assertEqual( p1 > p3, False) #Smaller by mass        
        self.assertEqual( p4 == p3 == p2, True)
        self.assertEqual( p1c == p1, True)
        self.assertEqual( p1c == p3, False) #Differ by mass
        self.assertEqual( p1d == p3, True) #Mass has been removed in p1d
        self.assertEqual( sq1 == p4, True) #Only common property for comparison is mass and zParity
        self.assertEqual( sq1 > p1, True)  #Larger by mass
        self.assertEqual( sq1 > sq2, True)  #Larger by mass
        self.assertEqual( sq1 == sq3, True)
        self.assertEqual( A == B, True)
        self.assertEqual( sq1 > B, False)  #Smaller by zParity
        self.assertEqual( u > d, True)  #Bigger by electric Charge
        self.assertEqual( u.chargeConjugate() > d, False)  #Smaller by electric Charge

    def testParticleList(self):
        l1 = ParticleList(particles=[A,B],label='Alist')
        L = particlesDict['L']
        l = particlesDict['l']
        self.assertEqual( str(l1) == 'Alist', True)
        self.assertEqual( l1.mass == B.mass, True)
        self.assertEqual( l > L, False) #L is longer
        self.assertEqual( l1 == A, True) #l1 contains A
        self.assertEqual( l1 == B, True) #l1 contains A
        
    def testParticleID(self):
        import smodels.particleDefinitions
        
        plist = smodels.particleDefinitions.MSSM
        setInternalID(plist)
        pNameDict = dict([[p._name,p] for p in plist])
        nue = pNameDict['nue']
        nueC = pNameDict['nue*']
        numu = pNameDict['numu']
        self.AssertNotEqual(nue._internalID,None)
        self.AssertEqual(nue._internalID,nueC._internalID)
        self.AssertEqual(nue._internalID,numu._internalID)
        self.AssertEqual(nue,numu)
        
        
        
        
        
            
if __name__ == "__main__":
    unittest.main()
