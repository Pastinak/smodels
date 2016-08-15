#!/usr/bin/env python

"""
.. module:: tools.modelTester
   :synopsis: Functions to test (a set of) points, handling decomposition,
              result and coverage checks, parallelisation.

.. moduleauthor:: Ursula Laa <Ursula.Laa@assoc.oeaw.ac.at>
.. moduleauthor:: Wolfgang Waltenberger <wolfgang.waltenberger@gmail.com>

"""

from smodels.tools import ioObjects
from smodels.tools import coverage, runtime
from smodels.theory import slhaDecomposer
from smodels.theory import lheDecomposer
from smodels.theory.theoryPrediction import theoryPredictionsFor
from smodels.tools import crashReport, timeOut
from smodels.tools.printer import MPrinter
import logging
import os
import sys
from ConfigParser import SafeConfigParser
from smodels.tools.physicsUnits import GeV, fb
from smodels.experiment.exceptions import DatabaseNotFoundException
from smodels.experiment.databaseObj import Database

log = logging.getLogger(__name__)

def testPoint(inputFile, outputDir, parser, databaseVersion, listOfExpRes):
    """
    Test model point defined in input file (running decomposition, check
    results, test coverage)

    :parameter inputFile: path to input file
    :parameter outputDir: path to directory where output is be stored
    :parameter parser: ConfigParser storing information from parameter.ini file
    :parameter databaseVersion: Database version (printed to output file)
    :parameter listOfExpRes: list of ExpResult objects to be considered
    """

    """Get run parameters and options from the parser"""
    sigmacut = parser.getfloat("parameters", "sigmacut") * fb
    minmassgap = parser.getfloat("parameters", "minmassgap") * GeV
    inputType = parser.get("options", "inputType").lower()


    """Setup output printers"""
    printerTypes = parser.get("stdout", "outputType").split(",")
    if isinstance(printerTypes,str):
        printerTypes = [printerTypes]
    masterPrinter = MPrinter(printerList=printerTypes)
    masterPrinter.setOutPutFiles(os.path.join(outputDir, os.path.basename(inputFile)))  
    

    """Check input file for errors"""
    inputStatus = ioObjects.FileStatus()
    if parser.getboolean("options", "checkInput"):
        inputStatus.checkFile(inputType, inputFile, sigmacut)
    """Initialize output status and exit if there were errors in the input"""
    outputStatus = ioObjects.OutputStatus(inputStatus.status, inputFile,
            dict(parser.items("parameters")), databaseVersion)
    masterPrinter.addObj(outputStatus)              
    if outputStatus.status < 0:          
        masterPrinter.flush()
        return
    

    """
    Decompose input file
    ====================
    """
    try:
        """ Decompose input SLHA file, store the output elements in smstoplist """
        if inputType == 'slha':
            smstoplist = slhaDecomposer.decompose(inputFile, sigmacut,
                    doCompress=parser.getboolean("options", "doCompress"),
                    doInvisible=parser.getboolean("options", "doInvisible"),
                    minmassgap=minmassgap)
        else:
            smstoplist = lheDecomposer.decompose(inputFile,
                    doCompress=parser.getboolean("options", "doCompress"),
                    doInvisible=parser.getboolean("options", "doInvisible"),
                    minmassgap=minmassgap)
    except:
        """ Update status to fail, print error message and exit """
        outputStatus.updateStatus(-1)
        masterPrinter.flush()
        return

    """ Print Decomposition output.
        If no topologies with sigma > sigmacut are found, update status, write
        output file, stop running """
    if not smstoplist:
        outputStatus.updateStatus(-3)
        masterPrinter.flush()
        return

    outLevel = 0
    if parser.getboolean("stdout", "printDecomp"):
        outLevel = 1
        outLevel += parser.getboolean("stdout", "addElmentInfo")
    masterPrinter.addObj(smstoplist,outLevel)
    
    for expResult in listOfExpRes: masterPrinter.addObj(expResult,outLevel)

    """
    Compute theory predictions
    ====================================================
    """

    """ Get theory prediction for each analysis and print basic output """
    allPredictions = []
    for expResult in listOfExpRes:
        theorypredictions = theoryPredictionsFor(expResult, smstoplist)
        if not theorypredictions: continue
        allPredictions += theorypredictions._theoryPredictions

    """ Define result list that collects all theoryPrediction objects."""
    maxcond = parser.getfloat("parameters", "maxcond")
    results = ioObjects.ResultList(allPredictions,maxcond)
    if not parser.getboolean("file", "expandedSummary"):
        results.useBestResult()

    outLevel = 0
    if not results.isEmpty():
        outputStatus.updateStatus(1)
        outLevel = 1
        outLevel += parser.getboolean("file", "addConstraintInfo")
        masterPrinter.addObj(results,outLevel)
    else:
        outputStatus.updateStatus(0) # no results after enforcing maxcond

    if parser.getboolean("options", "testCoverage"):
        """ Testing coverage of model point, add results to the output file """
        uncovered = coverage.Uncovered(smstoplist)
        masterPrinter.addObj(uncovered,2)
    
    masterPrinter.flush()

def runSingleFile(inputFile, outputDir, parser, databaseVersion, listOfExpRes,
                    timeout, development, parameterFile):
    """
    Call testPoint on inputFile, write crash report in case of problems

    :parameter inputFile: path to input file
    :parameter outputDir: path to directory where output is be stored
    :parameter parser: ConfigParser storing information from parameter.ini file
    :parameter databaseVersion: Database version (printed to output file)
    :parameter listOfExpRes: list of ExpResult objects to be considered
    :parameter crashReport: if True, write crash report in case of problems
    :param timeout: set a timeout for one model point (0 means no timeout)
    """
    try:
        with timeOut.Timeout(timeout):
            testPoint(inputFile, outputDir, parser, databaseVersion,
                                 listOfExpRes)
    except Exception,e:
        crashReportFacility = crashReport.CrashReport()
         
        if development:
            print(crashReport.createStackTrace())
            raise e
        else:
            print(crashReport.createStackTrace())
            crashReportFacility.createCrashReportFile( inputFile, parameterFile )
            print(crashReportFacility.createUnknownErrorMessage())


def runSetOfFiles(inputFiles, outputDir, parser, databaseVersion, listOfExpRes,
                    timeout, development, parameterFile):
    """
    Loop over all input files in inputFiles with testPoint

    :parameter inputFiles: list of input files to be tested
    :parameter outputDir: path to directory where output is be stored
    :parameter parser: ConfigParser storing information from parameter.ini file
    :parameter databaseVersion: Database version (printed to output file)
    :parameter listOfExpRes: list of ExpResult objects to be considered
    :parameter development: turn on development mode (e.g. no crash report)
    :parameter parameterFile: parameter file, for crash reports
    """
    for inputFile in inputFiles:
        runSingleFile(inputFile, outputDir, parser, databaseVersion,
                       listOfExpRes, timeout, development, parameterFile)

def testPoints(fileList, inDir, outputDir, parser, databaseVersion,
                 listOfExpRes, timeout, development, parameterFile):
    """
    Loop over all input files in fileList with testPoint, using ncpus CPUs
    defined in parser

    :param fileList: list of input files to be tested
    :param inDir: path to directory where input files are stored
    :param outputDir: path to directory where output is stored
    :param parser: ConfigParser storing information from parameter.ini file
    :param databaseVersion: Database version (printed to output files)
    :param listOfExpRes: list of ExpResult objects to be considered
    :param timeout: set a timeout for one model point (0 means no timeout)
    :param development: turn on development mode (e.g. no crash report)
    :param parameterFile: parameter file, for crash reports
    """

    if len( fileList ) == 0:
        log.error ( "no files given." )
        return
    if len(fileList ) == 1:
        runSingleFile ( fileList[0], outputDir, parser, databaseVersion,
                        listOfExpRes, timeout, development, parameterFile )
        return

    """ loop over input files and run SModelS """
    ncpusAll = runtime.nCPUs()
    ncpus = parser.getint("parameters", "ncpus")
    if ncpus < 1 or ncpus > ncpusAll: ncpus = ncpusAll
    log.info ("Running SModelS on %d cores" % ncpus )

    cleanedList = []
    for f in fileList:
        tmp = os.path.join(inDir, f )
        if not os.path.isfile ( tmp ):
            log.info ( "%s does not exist or is not a file. Skipping it." % tmp )
            continue
        cleanedList.append( tmp )

    if ncpus == 1:
        runSetOfFiles( cleanedList, outputDir, parser, databaseVersion,
                        listOfExpRes, timeout, development, parameterFile )
        return

    ### now split up for every fork
    chunkedFiles = [cleanedList[x::ncpus] for x in range(ncpus)]
    children = []
    for (i,chunk) in enumerate(chunkedFiles):
        pid=os.fork()
        log.debug("Forking: ",i,pid,os.getpid())
        if pid == 0:
            log.info("chunk #%d: pid %d (parent %d)." %
                    ( i, os.getpid(), os.getppid() ) )
            log.info( " `-> %s" % " ".join ( chunk ) )
            runSetOfFiles(chunk, outputDir, parser, databaseVersion, 
                            listOfExpRes, timeout, development, parameterFile)
            os._exit(0) ## not sys.exit(), return, nor continue
        if pid < 0:
            log.error ( "fork did not succeed! Pid=%d" % pid )
            sys.exit()
        if pid > 0:
            children.append ( pid )
    for child in children:
        r = os.waitpid ( child, 0 )
        log.info ( "child %d terminated: %s" % (child,r) )
    log.info ( "all children terminated" )

def loadDatabase(parser, db, verbosity):
    """
    Load database
    
    :parameter parser: ConfigParser with path to database
    :parameter db: binary database object
    :parameter verbosity: Verbosity when loading database
    :returns: database object, database version
        
    """
    try:
        databasePath = parser.get("path", "databasePath")
        database = db
        if database in [ None, True ]:
            force_load=None
            if database == True: force_load="txt"
            database = Database( databasePath, force_load=force_load,
                                 verbosity=verbosity )
        databaseVersion = database.databaseVersion
    except DatabaseNotFoundException:
        log.error("Database not found in %s" % os.path.realpath(databasePath))
        sys.exit()
    return database, databaseVersion

def loadDatabaseResults(parser, database):
    """
    Load database entries specified in parser
    
    :parameter parser: ConfigParser, containing analysis and txnames selection
    :parameter database: Database object
    :returns: List of experimental results
        
    """
    """ In case that a list of analyses or txnames are given, retrieve list """
    analyses = parser.get("database", "analyses").split(",")
    txnames = parser.get("database", "txnames").split(",")
    if parser.get("database", "dataselector") == "efficiencyMap":
        dataTypes = ['efficiencyMap']
        datasetIDs = ['all']
    elif parser.get("database", "dataselector") == "upperLimit":
        dataTypes = ['upperLimit']
        datasetIDs = ['all']
    else:
        dataTypes = ['all']
        datasetIDs = parser.get("database", "dataselector").split(",")

    """ Load analyses """

    ret = database.getExpResults(analysisIDs=analyses, txnames=txnames, datasetIDs=datasetIDs, dataTypes=dataTypes)
    """ Print list of analyses loaded """
    outLevel = 0
    if parser.getboolean("stdout", "printAnalyses"):
        outLevel = 1
        outLevel += parser.getboolean("stdout", "addAnaInfo")
    return ret

def getParameters(parameterFile):
    """
    Read parameter file, exit in case of errors
    
    :parameter parameterFile: Path to parameter File
    :returns: ConfigParser read from parameterFile
        
    """
    parser = SafeConfigParser()
    ret=parser.read(parameterFile)
    if ret == []:
        log.error ( "No such file or directory: '%s'" % parameterFile )
        sys.exit()
    return parser

def getAllInputFiles(inFile):
    """
    Given inFile, return list of all input files
    
    :parameter inFile: Path to input file or directory containing input files
    :returns: List of all input files
        
    """
    if os.path.isdir(inFile):
        fileList = os.listdir(inFile)
    else: fileList = [inFile]
    return fileList