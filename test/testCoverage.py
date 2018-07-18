"""
.. module:: testReweighting
   :synopsis: Tests the function of smodels.theory.updateParticles 
.. moduleauthor:: Alicia Wongel <alicia.wongel@gmail.com>   
"""
import sys
sys.path.insert(0,"../")
import unittest
from smodels.theory.particle import Particle
from smodels.theory.branch import Branch
from smodels.tools.coverage import Uncovered
from smodels.theory.topology import TopologyList
from smodels.tools.physicsUnits import eV, GeV, TeV, pb, fb
from smodels.theory.element import Element
from smodels.theory.crossSection import XSectionList, XSection, XSectionInfo
from smodels.share.models import SMparticles, MSSMparticles

n1 = MSSMparticles.n1
n1.totalwidth = 0.*GeV
st1 = MSSMparticles.st1
st1.totalwidth = 2.*GeV
st2 = MSSMparticles.st2
st2.totalwidth = 10**(-15)*GeV
gluino = MSSMparticles.gluino
gluino.totalwidth = 1.*10**(-30)*GeV
t = SMparticles.t
b = SMparticles.b

class CoverageTest(unittest.TestCase):     
   
    def testFill(self):
       
        topolist = TopologyList()
        
        # prompt
        b1 = Branch()
        b1.particles = [[b,t]]
        b1.BSMparticles = [st1,n1]
        b1.setInfo()
        el1 = Element()
        el1.branches=[b1,b1]
        
        # long-lived
        b3 = Branch()
        b3.particles = []
        b3.BSMparticles = [gluino]
        b4 = Branch()
        b4.particles = [[b,t]]
        b4.BSMparticles = [st1,n1]
        b3.setInfo()
        b4.setInfo()
        el2 = Element()
        el2.branches=[b3,b4]
        
        # prompt and displaced
        b5 = Branch()
        b5.particles = [[t],[b,t]]
        b5.BSMparticles = [st2,st1,n1]
        b6 = Branch()
        b6.particles = [[b,t]]
        b6.BSMparticles = [st1,n1]
        b5.setInfo()
        b6.setInfo()
        el3 = Element()
        el3.branches=[b5,b6]
        
        
        w1 = XSectionList()
        w1.xSections.append(XSection())
        w1.xSections[0].info = XSectionInfo()
        w1.xSections[0].info.sqrts = 8.*TeV
        w1.xSections[0].info.label = '8 TeV'
        w1.xSections[0].info.order = 0
        w1.xSections[0].value = 10.*fb    
        el1.weight = w1
        el2.weight = w1
        el3.weight = w1
        
        topolist.addElement(el1)
        topolist.addElement(el2)
        topolist.addElement(el3)
        uncovered = Uncovered(topolist, sigmacut = 0.0*fb)
               
        self.assertEqual(len(uncovered.longLived.generalElements), 1)
        self.assertEqual(len(uncovered.displaced.generalElements), 1)
        self.assertEqual(len(uncovered.MET.generalElements), 2)
       
        self.assertAlmostEqual(uncovered.longLived.generalElements[0]._contributingElements[0].weight.getMaxXsec()/fb, 10.)
        self.assertAlmostEqual(uncovered.displaced.generalElements[0]._contributingElements[0].weight.getMaxXsec()/fb, 0.994945089066*10.)
        self.assertAlmostEqual(uncovered.MET.generalElements[0]._contributingElements[0].weight.getMaxXsec()/fb, 10.)
        self.assertAlmostEqual(uncovered.MET.generalElements[1]._contributingElements[0].weight.getMaxXsec()/fb, 0.00505491093358*10.)

        
        
    
    
if __name__ == "__main__":
    unittest.main()       