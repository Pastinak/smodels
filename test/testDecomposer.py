#!/usr/bin/env python3

"""
.. module:: testDecomposer
   :synopsis: Tests the ascii grapher.
              Depends also on lheReader, lheDecomposer.

.. moduleauthor:: Wolfgang Waltenberger <wolfgang.waltenberger@gmail.com>

"""
import unittest
import sys
sys.path.insert(0,"../")
from smodels.share.models.mssm import BSMList
from smodels.share.models.SMparticles import SMList
from smodels.theory.model import Model
from smodels.installation import installDirectory
from smodels.theory import decomposer
from smodels.theory.element import Element 
from smodels.tools.physicsUnits import GeV,pb,TeV,fb

class DecomposerTest(unittest.TestCase):

    def testDecomposerLHE(self):
   
        filename = "%sinputFiles/lhe/simplyGluino.lhe" %(installDirectory())  
        model = Model(BSMList,SMList,filename)
        model.updateParticles()
           
        topList = decomposer.decompose(model)
        self.assertTrue(len(topList.getElements()) == 1)
        element = topList.getElements()[0]
        el = Element("[[[q,q]],[[q,q]]]",finalState=['MET','MET'])
        self.assertTrue(el == element)
        bsmLabels = [[bsm.label for bsm in branch] for branch in element.getBSMparticles()]
        self.assertEqual(bsmLabels,[['gluino','N1']]*2)
        self.assertAlmostEqual(element.getMasses(),[[675.*GeV,200.*GeV]]*2)
        xsec = [xsec for xsec in element.weight if xsec.info.sqrts == 8.*TeV][0]
        xsec = xsec.value.asNumber(pb)        
        self.assertAlmostEqual(xsec,0.262,3)
  
  
    def testDecomposerSLHA(self):
  
        filename = "%sinputFiles/slha/simplyGluino.slha" %(installDirectory())  
        model = Model(BSMList,SMList,filename)
        model.updateParticles()
          
        topList = decomposer.decompose(model)
        self.assertTrue(len(topList.getElements()) == 1)
        element = topList.getElements()[0]
        el = Element("[[[q,q]],[[q,q]]]",finalState=['MET','MET'])
        self.assertTrue(el == element)
        bsmLabels = [[bsm.label for bsm in branch] for branch in element.getBSMparticles()]
        self.assertEqual(bsmLabels,[['gluino','N1']]*2)
        self.assertAlmostEqual(element.getMasses(),[[675.*GeV,200.*GeV]]*2)
        xsec = [xsec for xsec in element.weight if xsec.info.sqrts == 8.*TeV][0]
        xsec = xsec.value.asNumber(pb)
        self.assertAlmostEqual(element.weight[0].value.asNumber(pb),0.572,3)
  
   
    def testDecomposerLongLived(self):
    
        filename = "%sinputFiles/slha/longLived.slha" %(installDirectory())
        #Consider a simpler model
        newModel = [ptc for ptc in BSMList if not isinstance(ptc.pdg,list) and abs(ptc.pdg) in [1000015,1000022]] 
        model = Model(newModel,SMList,filename)
        model.updateParticles()
            
        topList = decomposer.decompose(model)
        self.assertTrue(len(topList.getElements()) == 10)
        expectedWeights = {str(sorted([['N1'],['N1']])).replace(' ','') : 0.020,
                           str(sorted([['sta_1'],['sta_1~']])).replace(' ','') : 0.26,
                           str(sorted([['sta_1'],['sta_1~','N1~']])).replace(' ','') : 0.13,
                           str(sorted([['sta_1~'],['sta_1','N1']])).replace(' ','') : 0.13,
                           str(sorted([['sta_1~','N1~'],['sta_1','N1']])).replace(' ','') : 0.065}
              
        for el in topList.getElements():
            bsmLabels = str(sorted([[bsm.label for bsm in branch] for branch in el.getBSMparticles()]))
            bsmLabels = bsmLabels.replace(' ','')
            xsec = el.weight.getXsecsFor(8.*TeV)[0].value.asNumber(fb)
            self.assertAlmostEqual(expectedWeights[bsmLabels], xsec,2)


    def testCompression(self):
        
        filename = "./testFiles/slha/higgsinoStop.slha" 
        model = Model(BSMList,SMList,filename)
        model.updateParticles(promptWidth=1e-12*GeV) #Force charginos/neutralinos to be considered as prompt
        
        
        tested = False
        topos = decomposer.decompose(model, sigcut=0.1*fb, doCompress=False, doInvisible=False, minmassgap=5.*GeV )
        toposExpected = {'[][1]' : 1,'[][2]' : 14,'[1][1]' : 1,'[1][2]' : 25,'[2][2]' : 72,
                         '[][2,2]' : 44,'[1][1,1]' : 2,'[1][1,2]' : 22,'[2][1,2]' : 48,
                         '[2][2,2]' : 284,'[1,1][1,1]' : 5,'[1,1][1,2]' : 22,'[1,2][1,2]' : 120,
                         '[1][1,1,1]' : 2,'[1][1,2,2]' : 64,'[1,1][1,1,1]' : 12,'[1,1][1,1,2]' : 16,
                         '[1,2][1,2,2]' : 240,'[1,1,1][1,1,2]' : 56,'[1,1,2][1,1,2]' : 16,
                         '[1][1,1,1,2]' : 4,'[1,1][1,1,1,2]' : 56,'[1,1,2][1,1,1,2]' : 176}
        
        
        for topo in topos:
            self.assertEqual(len(topo.elementList),toposExpected[str(topo)])
            if str(topo)!="[1,1][1,1]":
                continue
            for element in topo.elementList:
                if str(element)!="[[[q],[W+]],[[t-],[t+]]]": 
                    continue
                tested = True
                self.assertEqual(element.motherElements[0][0],"original")
                self.assertEqual(len(element.motherElements),1)
        self.assertTrue(tested) #Make sure the test was performed
         
        tested = False
        topos = decomposer.decompose(model, sigcut=0.1*fb, doCompress=False, doInvisible=True, minmassgap=5.*GeV )
        toposExpected = {"[][]" : 1,"[][1]" : 2,"[][2]" : 22,"[1][1]" : 4,"[1][2]" : 25,"[2][2]" : 72,
                         "[][2,2]" : 44,"[1][1,1]" : 4,"[1][1,2]" : 42,"[2][1,2]" : 48,"[2][2,2]" : 284,
                         "[1,1][1,1]" : 5,"[1,1][1,2]" : 22,"[1,2][1,2]" : 120,"[1][1,1,1]" : 2,"[1][1,2,2]" : 72,
                         "[1,1][1,1,1]" : 20,"[1,1][1,1,2]" : 16,"[1,2][1,2,2]" : 240,"[1,1,1][1,1,2]" : 56,
                         "[1,1,2][1,1,2]" : 16,"[1][1,1,1,2]" : 4,"[1,1][1,1,1,2]" : 56,"[1,1,2][1,1,1,2]" : 176}
        for topo in topos:
            self.assertEqual(len(topo.elementList),toposExpected[str(topo)])
            if str(topo)!="[][]":
                continue
            for element in topo.elementList:
                if str(element) != "[[],[]]":
                    continue
                tested = True
                self.assertEqual(str(element.motherElements[0][1]),"[[],[[nu,nu]]]")
                bsmLabels = [[bsm.label for bsm in br] for br in element.getBSMparticles()]
                self.assertEqual(bsmLabels,[['N1'],['N2']])
                ## all neutrinos are considered as equal, so there should be a single mother:
                self.assertEqual(len(element.motherElements), 1) 
                self.assertEqual(str(element.motherElements[0][0]),"invisible" )
        self.assertTrue(tested) #Make sure the test was performed
         
         
        tested = False                 
        topos = decomposer.decompose(model, sigcut=0.1*fb, doCompress=True, doInvisible=False, minmassgap=5.*GeV)
        toposExpected = {"[][]" : 1,"[][1]" : 8,"[][2]" : 14,"[1][1]" : 4,"[1][2]" : 29,"[2][2]" : 72,
                        "[][1,2]" : 2,"[][2,2]" : 44,"[1][1,1]" : 4,"[1][1,2]" : 34,"[2][1,2]" : 48,
                        "[2][2,2]" : 284,"[1,1][1,1]" : 17,"[1,1][1,2]" : 22,"[1,2][1,2]" : 120,
                        "[1][1,1,1]" : 4,"[1][1,2,2]" : 64,"[1,1][1,1,1]" : 48,"[1,1][1,1,2]" : 16,
                        "[1,2][1,2,2]" : 240,"[1,1,1][1,1,2]" : 64,"[1,1,2][1,1,2]" : 16,"[1][1,1,1,2]" : 4,
                        "[1,1][1,1,1,2]" : 64,"[1,1,2][1,1,1,2]" : 176}
        for topo in topos:
            self.assertEqual(len(topo.elementList),toposExpected[str(topo)])
            if str(topo)!="[1][1]":
                continue
            for element in topo.elementList:
                if str(element)!="[[[b]],[[b]]]":
                    continue
                masses = element.motherElements[0][1].getMasses()
                dm = abs(masses[0][1]-masses[0][2])/GeV
                tested = True
                self.assertEqual(len(element.motherElements),24)
                self.assertEqual(str(element.motherElements[0][0]),"mass" )
                self.assertTrue(dm < 5.0)
        self.assertTrue(tested) #Make sure the test was performed
                        
        tested = False                 
        topos = decomposer.decompose(model, sigcut=0.1*fb, doCompress=True, doInvisible=True, minmassgap=5.*GeV )
        el1 = Element("[[[b]],[[b]]]",finalState=['MET','MET'])
        el1.elID = [541, 542, 543, 544, 545, 546, 547, 548, 561, 562, 563, 
                  564, 571, 572, 573, 580, 581, 582, 589, 590, 597, 598, 605, 612] 
        el2 = Element("[[[b]],[[t+]]]",finalState=['MET','MET'])
        el2.elID = [160, 161, 162, 163, 164, 755, 756, 757, 758, 759, 760, 761, 
                  762, 763, 764, 765, 766, 767, 768, 769, 770, 771, 772, 773, 
                  774, 775, 776, 777, 778, 779, 780, 781, 782, 783, 784, 785, 
                  786, 839, 840, 841, 842, 843, 844, 845, 846, 847, 848, 849, 
                  850, 851, 852, 853, 854, 855, 856, 857, 858, 879, 880, 881, 
                  882, 883, 884, 885, 886, 887, 888, 889, 890, 891, 892, 893, 
                  894, 895, 896, 897, 898, 903, 904, 905, 906, 907, 908, 909, 
                  910, 911, 912, 913, 914, 915, 916, 917, 918, 919, 920, 921, 
                  922, 923, 924, 925, 926, 927, 928, 929, 930, 931, 932, 933, 
                  934, 935, 936, 937, 938]

        el3 = Element("[[[b]],[[t+]]]",finalState=['MET','MET'])
        el3.elID = [577, 609, 552, 616, 594]
        el4 = Element("[[[b]],[[t-]]]",finalState=['MET','MET'])
        el4.elID = [171, 172, 173, 174, 175, 787, 788, 789, 790, 791, 792, 793, 
                  794, 795, 796, 797, 798, 799, 800, 801, 802, 803, 804, 805, 
                  806, 807, 808, 809, 810, 811, 812, 813, 814, 815, 816, 817, 
                  818, 819, 820, 821, 822, 823, 824, 825, 826, 827, 828, 829, 
                  830, 831, 832, 833, 834, 835, 836, 837, 838, 859, 860, 861, 
                  862, 863, 864, 865, 866, 867, 868, 869, 870, 871, 872, 873, 
                  874, 875, 876, 877, 878, 899, 900, 901, 902, 939, 940, 941, 
                  942, 943, 944, 945, 946, 947, 948, 949, 950, 951, 952, 953, 
                  954, 955, 956, 957, 958, 959, 960, 961, 962, 963, 964, 965, 
                  966, 967, 968, 969, 970]
        el5 = Element("[[[b]],[[t-]]]",finalState=['MET','MET'])
        el5.elID = [586, 622, 558, 568, 602]
        el6 = Element("[[[t+]],[[t-]]]",finalState=['MET','MET'])
        el6.elID = [16, 663, 664, 665, 666, 667, 668, 669, 670, 671, 672, 673, 
                  674, 675, 676, 677, 678, 679, 680, 681, 682, 683, 684, 685, 
                  686, 687, 688, 689, 690, 691, 692, 693, 694, 695, 696, 697, 
                  698, 699, 700, 701, 702, 703, 704, 705, 706, 707, 708, 709, 
                  710, 711, 712, 713, 714, 715, 716, 717, 718, 719, 720, 721, 
                  722, 723, 724, 725, 726]
        el7 = Element("[[[t+]],[[t-]]]",finalState=['MET','MET'])
        el7.elID = [168, 987, 988, 989, 990]
        el8 = Element("[[[t+]],[[t-]]]",finalState=['MET','MET'])
        el8.elID = [975, 976, 977, 978, 179]
        el9 = Element("[[[t+]],[[t-]]]",finalState=['MET','MET'])
        el9.elID = [646]
        elementsExpected = [el1,el2,el3,el4,el5,el6,el7,el8,el9]
        elIDs = [el.elID for el in elementsExpected]
        toposExpected = {"[][]" : 2,"[][1]" : 9,"[][2]" : 14,"[1][1]" : 9,"[1][2]" : 29,
                         "[2][2]" : 72,"[][1,2]" : 2,"[][2,2]" : 44,"[1][1,1]" : 6,"[1][1,2]" : 44,
                         "[2][1,2]" : 48,"[2][2,2]" : 284,"[1,1][1,1]" : 17,"[1,1][1,2]" : 22,
                         "[1,2][1,2]" : 120,"[1][1,1,1]" : 4,"[1][1,2,2]" : 72,"[1,1][1,1,1]" : 56,
                         "[1,1][1,1,2]" : 16,"[1,2][1,2,2]" : 240,"[1,1,1][1,1,2]" : 64,
                         "[1,1,2][1,1,2]" : 16,"[1][1,1,1,2]" : 4,"[1,1][1,1,1,2]" : 64,
                         "[1,1,2][1,1,1,2]" : 176}
        for topo in topos:
            self.assertEqual(len(topo.elementList),toposExpected[str(topo)])
            if str(topo)!="[1][1]":
                continue            
            for element in topo.elementList:
                tested = True
                iel = elIDs.index(element.elID)
                self.assertEqual(element,elementsExpected[iel])
        self.assertTrue(tested) #Make sure the test was performed
        
if __name__ == "__main__":
    unittest.main()