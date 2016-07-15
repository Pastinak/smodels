#!/usr/bin/env python

"""
.. module:: testPrinter
   :synopsis: Tests printer facilities with runSModelS

.. moduleauthor:: Andre Lessa <lessa.a.p@gmail.com>

"""

import sys,shutil,os
sys.path.insert(0,"../")
import unittest
from smodels.installation import installDirectory as idir
from smodels.theory import slhaDecomposer
from smodels.tools.physicsUnits import fb, GeV, TeV
from smodels.theory.theoryPrediction import theoryPredictionsFor
from smodels.tools import printer, ioObjects
from smodels.tools import coverage
from smodels.tools import summaryReader
from xml.etree import ElementTree
import logging
from databaseLoader import database
import unum

def equalObjs(obj1,obj2,allowedDiff,ignore=[]):
    """
    Compare two objects.
    The numerical values are compared up to the precision defined by allowedDiff.
    
    :param obj1: First python object to be compared 
    :param obj2: Second python object to be compared
    :param allowedDiff: Allowed % difference between two numerical values 
    :param ignore: List of keys to be ignored
    :return: True/False    
    """      
    
    if type(obj1) != type(obj2):
        logger.info("Data types differ (%s,%s)" %(type(obj1),type(obj2)))
        return False
    
    if isinstance(obj1,unum.Unum):
        if obj1 == obj2:
            return True
        diff = 2.*abs(obj1-obj2)/abs(obj1+obj2)
        return diff.asNumber() < allowedDiff
    elif isinstance(obj1,float):        
        if obj1 == obj2:
            return True
        diff = 2.*abs(obj1-obj2)/abs(obj1+obj2)
        return diff < allowedDiff
    elif isinstance(obj1,str):
        return obj1 == obj2
    elif isinstance(obj1,dict):    
        for key in obj1:
            if key in ignore: continue
            if not key in obj2:
                logger.warning("Key %s missing" %key)
                return False
            if not equalObjs(obj1[key],obj2[key],allowedDiff):
                logger.warning('Objects differ:\n   %s\n and\n   %s' %(str(obj1[key]),str(obj2[key])))
                return False
    elif isinstance(obj1,list):
        for ival,val in enumerate(sorted(obj1)):
            if not equalObjs(val,sorted(obj2)[ival],allowedDiff):
                logger.warning('Objects differ:\n   %s \n and\n   %s' %(str(val),str(sorted(obj2)[ival])))
                return False
    else:
        return obj1 == obj2
            
    return True



class RunPrinterTest(unittest.TestCase):

    def __init__ ( self, *args, **kwargs):
        super(RunPrinterTest, self).__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)
        
        self.masterPrinter = printer.MPrinter(printerList=['stdout','summary','python','xml'])        
        #Set the address of the database folder
        self.slhafile = os.path.join ( idir(), "inputFiles/slha/gluino_squarks.slha" )
        self.masterPrinter.setOutPutFiles('./unitTestOutput/printer_output')
        self.runMain()


    def runMain(self):
        """
        Main program. Displays basic use case.
    
        """

        #Set main options for decomposition:
        sigmacut = 0.03 * fb
        mingap = 5. * GeV
    
        """ Decompose model (use slhaDecomposer for SLHA input or lheDecomposer
            for LHE input) """
        smstoplist = slhaDecomposer.decompose(self.slhafile, sigmacut, 
                         doCompress=True, doInvisible=True, minmassgap=mingap )
    
        #Add the decomposition result to the printers
        self.masterPrinter.addObj(smstoplist)
    
        listOfExpRes = database.getExpResults()
        # Compute the theory predictions for each analysis
        allPredictions = []
        for expResult in listOfExpRes:
            predictions = theoryPredictionsFor(expResult, smstoplist)
            if not predictions:
                continue
            allPredictions += predictions._theoryPredictions
        
        maxcond = 0.2
        results = ioObjects.ResultList(allPredictions,maxcond)
        self.masterPrinter.addObj(results,objOutputLevel=2)
        
        #Add coverage information:
        coverageInfo = coverage.Uncovered(smstoplist)
        self.masterPrinter.addObj(coverageInfo,3)
        
        
        #Add additional information:
        databaseVersion = database.databaseVersion
        outputStatus = ioObjects.OutputStatus([1,None], self.slhafile,
                                               {'sigmacut' : sigmacut.asNumber(fb), 
                                                'minmassgap' : mingap.asNumber(GeV),
                                                'maxcond': maxcond },
                                              databaseVersion)
        outputStatus.status = 1
        self.masterPrinter.addObj(outputStatus)
        self.masterPrinter.flush()

    def testTextPrinter(self):
        outputfile = os.path.join ( idir(), "test/unitTestOutput/printer_output.smodels" )
        samplefile = os.path.join ( idir(), "test/summary_default.txt" )
        #Test summary output
        output = summaryReader.Summary( outputfile )
        sample = summaryReader.Summary( samplefile )
        try:
            self.assertEquals(sample, output)
        except AssertionError,e:
            msg = "%s != %s" % ( sample, output ) 
            raise AssertionError ( msg )


    def testPythonPrinter(self):
        #Test python output
        shutil.copyfile('./unitTestOutput/printer_output.py','./output.py')
        from gluino_squarks_default import smodelsOutputDefault        
        from output import smodelsOutput
        ignoreFields = ['input file','smodels version']
        equals = equalObjs(smodelsOutput,smodelsOutputDefault,allowedDiff=0.01,ignore=ignoreFields)
        self.assertEqual(equals,True)
        os.remove('./output.py')
        os.remove('./output.pyc')



#     def testXmlPrinter(self):
#         defFile = os.path.join ( idir(), "test/default_output.xml" )
#         outFile = os.path.join ( idir(), "test/unitTestOutput/printer_output.xml" )
#         
#         #Test xml output
#         xmlDefault = ElementTree.parse( defFile ).getroot()
#         xmlNew = ElementTree.parse( outFile ).getroot()
#         def compareXML(xmldefault,xmlnew):
#             self.assertEqual(len(xmldefault),len(xmlnew))
#             for i,el in enumerate(xmldefault):
#                 newel = xmlnew[i]
#                 self.assertEqual(len(el),len(newel))                
#                 if len(el) == 0:
#                     if el.tag == 'input_file': continue
#                     self.assertEqual(el.text,newel.text)
#                     self.assertEqual(el.tag,newel.tag)
#                 else:                    
#                     compareXML(el,newel)
#         try:
#             compareXML(xmlDefault,xmlNew)
#         except AssertionError,e:
#             msg = "%s != %s" % ( defFile, outFile )
#             raise AssertionError ( msg )


if __name__ == "__main__":
    unittest.main()
