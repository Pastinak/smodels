#!/usr/bin/env python

"""
.. module:: testBranchClass
   :synopsis: Tests the theory.particle.Branch class

.. moduleauthor:: Andre Lessa <lessa.a.p@gmail.com>

"""
import sys
sys.path.insert(0,"../")
from smodels.theory.exceptions import SModelSTheoryError
import unittest
from smodels.theory.particle import Particle
from smodels.theory.vertex import Vertex
from smodels.theory.branch import Branch,createBranchFromStr,decayBranches
from smodels.tools.physicsUnits import GeV, fb



g = Particle(mass=500.*GeV,_pid=1000021, zParity=-1)
sq1 = Particle(mass = 150.*GeV, zParity = -1,_pid=1000005)
sq2 = Particle(mass = 100.*GeV, zParity = -1,_pid=2000005)
sq2b = Particle(mass = 100.*GeV, zParity = -1, _pid = 1000004)
sn1 = Particle(name='neutralino1', mass = 50.*GeV, zParity = -1, _pid = 1000022)
u = Particle(name='u', zParity = 1, _pid = 3)
d = Particle(name='d',mass = 0.01*GeV, zParity = 1, _pid = 2)



class BranchTest(unittest.TestCase):
        
    def testBranch(self):
        
        v1 = Vertex(inParticle=g, outParticles=[sq1,u,d])
        v2 = Vertex(inParticle=sq1, outParticles=[sq2,d])
        v2b = Vertex(inParticle=sq1, outParticles=[sq2b,d])
        v3 = Vertex(inParticle=sq2, outParticles=[d,u,sn1])
        v4 = Vertex(inParticle=sq1, outParticles=[d,u,sn1])
        b1 = Branch(vertices = [v1,v2,v3])
        b1b = Branch(vertices = [v1,v2b,v3])
        b2 = Branch(vertices = [v2,v3])
        b3 = Branch(vertices = [v1,v3])
        b4 = Branch(vertices = [v1,v4])
        
        self.assertEqual( str(b1) == '[[d,u],[d],[d,u]]', True)
        self.assertEqual( b1 == b1b, True)
        self.assertEqual(b1 > b2, True)  #Larger by number of vertices
        self.assertEqual(b2 > b3, False)  #Smaller by number of outgoing particles
        self.assertEqual(b3 > b4, False)  #Smaller by mass of sq2
        self.assertEqual(len(b1) == 3, True)
        
    def testBranchStr(self):
        
        v1 = Vertex(inParticle=g, outParticles=[sq1,u,d])
        v2 = Vertex(inParticle=sq1, outParticles=[sq2,d])
        v3 = Vertex(inParticle=sq2, outParticles=[d,u,sn1])
        b1 = Branch(vertices = [v1,v2,v3])
        
        bstr = createBranchFromStr('[[u,d],[d],[u,d]]')
        self.assertEqual( b1 == bstr, True)
        
    def testBranchAddVertex(self):
        
        v1 = Vertex(inParticle=g, outParticles=[sq1,u,d])
        v2 = Vertex(inParticle=sq1, outParticles=[sq2,d])
        v3 = Vertex(inParticle=sq2, outParticles=[d,u,sn1])
        b1 = Branch(vertices = [v1,v2])
        b2 = None
        try:
            b2 = b1._addVertex(v2)
        except SModelSTheoryError:
            pass
        self.assertEqual(b2 is None, True) #Should fail (incoming and outgoing do not match)
        
        b2 = b1._addVertex(v3)
        bstr = createBranchFromStr('[[u,d],[d],[u,d]]')
        self.assertEqual( b2 == bstr, True)
        
    def testBranchDecay(self):
        
        
        v1 = Vertex(inParticle=g, outParticles=[sq1,u,d])
        v1b = Vertex(inParticle=g, outParticles=[sq2,u,d])
        v2 = Vertex(inParticle=sq1, outParticles=[sq2,d])
        v2b = Vertex(inParticle=sq1, outParticles=[sq2,u])            
        v3 = Vertex(inParticle=sq2, outParticles=[d,u,sn1])
        
        v2.br = 0.1
        v2b.br = 0.9
        v3.br = 0.3
        
        vDict = {1000021 : [v1,v1b], 1000005 : [v2,v2b], 2000005 : [v3]}
        
        b1 = Branch(vertices = [v1])
        b1b = Branch(vertices = [v1b])
        b1.maxWeight = 10.*fb
        b1b.maxWeight = 1.*fb
        bList = [Branch(vertices = [v1,v2,v3]),Branch(vertices = [v1,v2b,v3])
                 ,Branch(vertices = [v1b,v3])]
        bList[0].maxWeight = b1.maxWeight*v2.br*v3.br
        bList[1].maxWeight = b1.maxWeight*v2b.br*v3.br
        bList[2].maxWeight = b1b.maxWeight*v3.br             
        dList = decayBranches([b1,b1b],vDict)
        self.assertEqual(len(dList) == 3, True)
        self.assertEqual(sorted(bList) == sorted(dList), True)
        
        weightsA = [b.maxWeight for b in sorted(bList)]
        weightsB = [b.maxWeight for b in sorted(dList)]
        self.assertEqual(weightsA == weightsB, True)
        
    def testDecayBranches(self):
        
        
        v1 = Vertex(inParticle=g, outParticles=[sq1,u,d])
        v1b = Vertex(inParticle=g, outParticles=[sq2,u,d])
        v2 = Vertex(inParticle=sq1, outParticles=[sq2,d])
        v2b = Vertex(inParticle=sq1, outParticles=[sq2,u])            
        v3 = Vertex(inParticle=sq2, outParticles=[d,u,sn1])
        
        vDict = {1000021 : [v1,v1b], 1000005 : [v2,v2b], 2000005 : [v3]}
        
        b1 = Branch(vertices = [v1])
        b2L = [Branch(vertices = [v1,v2]),Branch(vertices = [v1,v2b])]
        b3L = [Branch(vertices = [v1,v2,v3])]
        
        d2L = b1.decay(vDict)
        self.assertEqual(len(d2L) == 2, True)
        self.assertEqual(sorted(d2L) == sorted(b2L), True)
        
        d3L = b2L[0].decay(vDict)
        self.assertEqual(len(d3L) == 1, True)
        self.assertEqual( d3L == b3L, True)                     
        
if __name__ == "__main__":
    unittest.main()
