#!/usr/bin/env python

"""
.. module:: testElementClass
   :synopsis: Tests the theory.element.Element class

.. moduleauthor:: Andre Lessa <lessa.a.p@gmail.com>

"""
import sys
sys.path.insert(0,"../")
import unittest
from smodels.theory.vertex import Vertex
from smodels.theory.branch import Branch
from smodels.theory.element import Element,createElementFromStr
from smodels.particleDefinitions import useParticlesNameDict
from smodels.tools.physicsUnits import GeV


u = useParticlesNameDict['u']
d = useParticlesNameDict['d']
t = useParticlesNameDict['t+']
bbar = useParticlesNameDict['b+']
g = useParticlesNameDict['g']
em = useParticlesNameDict['e-']
nue = useParticlesNameDict['nue']
L = useParticlesNameDict['L']
e = useParticlesNameDict['e']


gluino = useParticlesNameDict['gluino']
st1 = useParticlesNameDict['st_1']
n1 = useParticlesNameDict['N1']
n2 = useParticlesNameDict['N2']
n3 = useParticlesNameDict['N3']
n4 = useParticlesNameDict['N4']

class ElementTest(unittest.TestCase):
        
    def testElement(self):
        
        v0 = Vertex(inParticle=None, outParticles=[gluino])
        v0b = Vertex(inParticle=None, outParticles=[st1])
        v1 = Vertex(inParticle=gluino, outParticles=[st1,t])
        v2 = Vertex(inParticle=st1, outParticles=[n1,bbar,t])
        
        b1 = Branch(vertices=[v0,v1,v2])
        b2 = Branch(vertices=[v0b,v2])
        
        el1 = Element(branches=[b1,b2])        
        el2 = Element(branches=[b2,b2])
        el1B = Element()
        el1B.branches = [b2,b1]
        self.assertEqual(el1 > el2,True) #Bigger by number of vertices
        self.assertEqual(el1 == el1B,True) #Just differ br branch ordering
        
        e1Info = {"vertnumb" : [2,3], "vertparts" : [[1,3],[1,2,3]]}
        self.assertEqual(el1.getEinfo() == e1Info, True) 
        
        
    def testElementInclusive(self):
        
        v0 = Vertex(inParticle=None, outParticles=[gluino])
        v0b = Vertex(inParticle=None, outParticles=[st1])     
        v1 = Vertex(inParticle=gluino, outParticles=[st1,em])
        v2 = Vertex(inParticle=st1, outParticles=[n1,em,nue])

        v1b = Vertex(inParticle=gluino, outParticles=[st1,L])
        v2b = Vertex(inParticle=st1, outParticles=[n1,L,nue])
        
        b1 = Branch(vertices = [v0,v1,v2])
        b1b = Branch(vertices = [v0,v1b,v2b])
        b2 = Branch(vertices=[v0b,v2b])
        b2b = Branch(vertices=[v0b,v2])
        
        el1 = Element(branches = [b1,b2])
        el2 = Element()
        el2.branches = [b2b,b1b]
        
        self.assertEqual( el1 == el2, True) #Test if inclusive label comparison works
        
    def testElementStr(self):
        
        v0 = Vertex(inParticle=None, outParticles=[gluino])
        v0b = Vertex(inParticle=None, outParticles=[st1])
        v1 = Vertex(inParticle=gluino, outParticles=[st1,t])
        v2 = Vertex(inParticle=st1, outParticles=[n1,bbar,t])
        
        b1 = Branch(vertices=[v0,v1,v2])
        b2 = Branch(vertices=[v0b,v2])
        
        el1 = Element(branches=[b1,b2])
                        
        elstrA = createElementFromStr('[[[t+],[b+,t+]],[[b+,t+]]]')
        elstrB = createElementFromStr('[[[b+,t+]],[[t+],[b+,t+]]]')
        elstrC = createElementFromStr('[[[b,t+]],[[t],[b+,t]]]')
                
        self.assertEqual( el1 == elstrA, True) #Elements should be equal
        self.assertEqual( el1 == elstrB, True) #Elements should be equal (just switch branches)
        self.assertEqual( el1 == elstrC, True) #Elements should be equal (inclusive labels)
        
    def testElementMassComp(self):


        v0 = Vertex(inParticle=None, outParticles=[gluino])
        v0b = Vertex(inParticle=None, outParticles=[st1])
        v0c = Vertex(inParticle=None, outParticles=[n1])
        v1 = Vertex(inParticle=gluino, outParticles=[st1,t])
        v2 = Vertex(inParticle=st1, outParticles=[n1,bbar,t])
        v1c = Vertex(inParticle=gluino, outParticles=[n1,t])
        
        b1 = Branch(vertices=[v0,v1,v2])
        b2 = Branch(vertices=[v0b,v2])
        el1 = Element(branches=[b1,b2])
        
        #Compress gluino-stop1
        gluino.mass = 400.*GeV
        st1.mass = 398.*GeV
        n1.mass = 390.*GeV        
        el1Comp = el1.massCompress(minmassgap = 5.*GeV)
        b1Comp = Branch(vertices=[v0b,v2])
        b2Comp = b2
        el2 = Element(branches=[b1Comp,b2Comp])
        self.assertEqual( el1Comp == el2, True) #Elements should be equal
        
        
        #Compress stop1-neutralino1
        gluino.mass = 400.*GeV
        st1.mass = 393.*GeV
        n1.mass = 390.*GeV        
        el1Comp = el1.massCompress(minmassgap = 5.*GeV)

        b1Comp = Branch(vertices=[v0,v1c])
        b2Comp = Branch(vertices=[v0c])
        el2 = Element(branches=[b1Comp,b2Comp])
        self.assertEqual( el1Comp == el2, True) #Elements should be equal        

        
        #Compress everything
        el1Comp = el1.massCompress(minmassgap = 10.*GeV) #Fully compress
        b1Comp = Branch(vertices=[v0c])
        b2Comp = Branch(vertices=[v0c])
        el2 = Element(branches=[b1Comp,b2Comp])        
        self.assertEqual( el1Comp == el2, True) #Elements should be equal  
        

    def testElementInvComp(self):
          
        gluino.mass = 500.*GeV
        st1.mass = 400.*GeV
        n1.mass = 300.*GeV
        n2.mass = 310.*GeV
        n3.mass = 320.*GeV 
        n4.mass = 330.*GeV  
          
        v0 = Vertex(inParticle=None, outParticles=[gluino])        
        v0c = Vertex(inParticle=None, outParticles=[n3])
        v1 = Vertex(inParticle=gluino, outParticles=[st1,t])
        v2 = Vertex(inParticle=st1, outParticles=[n3,t])
        v3 = Vertex(inParticle=n3, outParticles=[n1,nue,nue])        
        v4 = Vertex(inParticle=n3, outParticles=[n2,nue])
        v5 = Vertex(inParticle=n2, outParticles=[n1,nue,nue,nue,nue])
        v6 = Vertex(inParticle=n2, outParticles=[n1,nue,nue,nue,em])
          

         
        #Compress one step:
        #N3 --> N1 + [nue,nue]
        #gluino --> st_1 + [t+]/st_1 --> N3 + [t+]/N3 --> N1 + [nue,nue]
        b1 = Branch(vertices=[v0,v1,v2,v3])
        b2 = Branch(vertices=[v0c,v3])
        el1 = Element(branches=[b1,b2])
        el1Comp = el1.invisibleCompress()                 
        b1Comp = Branch(vertices=[v0,v1,v2])
        b2Comp = Branch(vertices=[v0c])
        el2 = Element(branches=[b1Comp,b2Comp])
        self.assertEqual( el1Comp == el2, True) #Elements should be equal

        #Compress two steps:
        #N3 --> N1 + [nue,nue]
        #gluino --> st_1 + [t+]/st_1 --> N3 + [t+]/N3 --> N2 + [nue]/N2 --> N1 + [nue,nue,nue,nue]
        b1 = Branch(vertices=[v0,v1,v2,v4,v5])
        b2 = Branch(vertices=[v0c,v3])
        el1 = Element(branches=[b1,b2])
        el1Comp = el1.invisibleCompress()                 
        b1Comp = Branch(vertices=[v0,v1,v2])
        b2Comp = Branch(vertices=[v0c])
        el2 = Element(branches=[b1Comp,b2Comp])
        self.assertEqual( el1Comp == el2, True) #Elements should be equal
        
        #Make sure compression only happens at the end:
        #N3 --> N1 + [nue,nue]
        #gluino --> st_1 + [t+]/st_1 --> N3 + [t+]/N3 --> N2 + [nue]/N2 --> N1 + [e-,nue,nue,nue]
        b1 = Branch(vertices=[v0,v1,v2,v4,v6])
        b2 = Branch(vertices=[v0c,v3])
        el1 = Element(branches=[b1,b2])
        el1Comp = el1.invisibleCompress()                 
        b1Comp = Branch(vertices=[v0,v1,v2,v4,v6])
        b2Comp = Branch(vertices=[v0c])
        el2 = Element(branches=[b1Comp,b2Comp])
        self.assertEqual( el1Comp == el2, True) #Elements should be equal

        
if __name__ == "__main__":
    unittest.main()
