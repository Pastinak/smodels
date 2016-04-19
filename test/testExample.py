#!/usr/bin/env python

"""
.. module:: testExample
   :synopsis: Tests a simple full smodels run

.. moduleauthor:: Andre Lessa <lessa.a.p@gmail.com>

"""
import sys
sys.path.insert(0,"../")
import unittest
from smodels.tools.physicsUnits import GeV, fb
from smodels.theory import decomposer
from smodels.theory.theoryPrediction import theoryPredictionsFor
from smodels.experiment.databaseObj import Database
from smodels.particleDefinitions import useParticlesNameDict

class ExampleTest(unittest.TestCase):        
    def testExample(self):
        """
        Main program. Displays basic use case.
    
        """
        
        #Path to input file name (either a SLHA or LHE file)
        slhafile = '../inputFiles/slha/lightEWinos.slha'
    
        #Set main options for decomposition:
        sigmacut = 0.3 * fb
        mingap = 5. * GeV
    
        """ Decompose model (use slhaDecomposer for SLHA input or lheDecomposer for LHE input) """
        smstoplist = decomposer.decompose(slhafile, sigmacut, doCompress=True, 
                                          doInvisible=True, minmassgap=mingap)
        # smstoplist = lheDecomposer.decompose(lhefile, doCompress=True,doInvisible=True, minmassgap=mingap)
        for top in smstoplist:
            if str(top) != '[1,2][1,3,3]': continue
            print top.getElements()[0]
            print top.getElements()[0].describe()
            print top.getElements()[0].weight[0].value
        N3 = useParticlesNameDict['N3']
        print  N3._width
        for v in  N3._decayVertices:
            print v.describe()
        self.assertEqual(len(smstoplist), 23)        
        self.assertEqual(len(smstoplist.getElements()), 586)
        # Load all analyses from database
        
        database = Database("./database/")
        listOfExpRes = database.getExpResults()
        self.assertEqual(len(listOfExpRes), 4)
        
        
        sys.exit()
        # Compute the theory predictions for each analysis
        for expResult in listOfExpRes:
            predictions = theoryPredictionsFor(expResult, smstoplist)
            if not predictions: continue
            print('\n',expResult.getValuesFor('id')[0])
            for theoryPrediction in predictions:
                dataset = theoryPrediction.dataset
                datasetID = dataset.getValuesFor('dataId')[0]            
                mass = theoryPrediction.mass
                txnames = [str(txname) for txname in theoryPrediction.txnames]
                PIDs =  theoryPrediction.PIDs         
                print("------------------------")
                print("Dataset = ",datasetID)   #Analysis name
                print("TxNames = ",txnames)   
                print("Prediction Mass = ",mass)    #Value for average cluster mass (average mass of the elements in cluster)
                print("Prediction PIDs = ",PIDs)    #Value for average cluster mass (average mass of the elements in cluster)
                print("Theory Prediction = ",theoryPrediction.value)   #Value for the cluster signal cross-section
                print("Condition Violation = ",theoryPrediction.conditions)  #Condition violation values
                  
                #Get upper limit for the respective prediction:
                if expResult.getValuesFor('dataType')[0] == 'upperLimit':
                    ul = expResult.getUpperLimitFor(txname=theoryPrediction.txnames[0],mass=mass)                     
                elif expResult.getValuesFor('dataType')[0] == 'efficiencyMap':
                    ul = expResult.getUpperLimitFor(dataID=datasetID)
                else: print('weird:',expResult.getValuesFor('dataType'))
                print("Theory Prediction UL = ",ul)
                print("R = ",theoryPrediction.value[0].value/ul)
          
        

        
if __name__ == "__main__":
    unittest.main()

