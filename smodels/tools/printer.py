"""
.. module:: printer
   :synopsis: Facility used to print elements, theorypredictions, missing topologies et al
      in various forms

.. moduleauthor:: Wolfgang Magerl <wolfgang.magerl@gmail.com>
.. moduleauthor:: Ursula Laa <ursula.laa@lpsc.in2p3.fr>
.. moduleauthor:: Suchita Kulkanri <suchita.kulkarni@gmail.com>
.. moduleauthor:: Andre Lessa <lessa.a.p@gmail.com>

"""

from __future__ import print_function
import sys,os
from smodels.theory.topology import TopologyList
from smodels.theory.theoryPrediction import TheoryPredictionList
from smodels.experiment.databaseObj import ExpResultList
from smodels.tools.ioObjects import OutputStatus
from smodels.tools.coverage import Uncovered
from smodels.tools.physicsUnits import GeV, fb, TeV
from smodels.tools.smodelsLogging import logger
import numpy as np
from collections import OrderedDict
from xml.dom import minidom
from xml.etree import ElementTree
import unum
import time

class MPrinter(object):
    """
    Master Printer class to handle the Printers (one printer/output type)
    """

    def __init__(self):

        self.name = "master"
        self.Printers = {}

    def setPrinterOptions(self,parser):
        """
        Define the printer types and their options.

        :param parser: ConfigParser storing information from the parameters file
        """

        #Define the printer types and the printer-specific options:
        printerTypes = [prt.strip() for prt in parser.get("printer", "outputType").split(",")]
        for prt in printerTypes:
            if prt == 'python':
                newPrinter = PyPrinter(output = 'file')
            elif prt == 'summary':
                newPrinter = SummaryPrinter(output = 'file')
            elif prt == 'stdout':
                newPrinter = TxTPrinter(output = 'stdout')
            elif prt == 'log':
                newPrinter = TxTPrinter(output = 'file')
            elif prt == 'xml':
                newPrinter = XmlPrinter(output = 'file')
            elif prt == 'slha':
                newPrinter = SLHAPrinter(output = 'file')
                if parser.getboolean("options", "doCompress") or parser.getboolean("options", "doInvisible"):
                    newPrinter.docompress = 1
                if parser.getboolean("options", "combineSRs"):
                    newPrinter.combinesr = 1
            else:
                logger.warning("Unknown printer format: %s" %str(prt))
                continue

            #Copy stdout options to log options:
            if 'log' in printerTypes:
                if parser.has_section('stdout-printer') and not parser.has_section('log-printer'):
                    parser.add_section('log-printer')
                    for option,val in parser.items('stdout-printer'):
                        parser.set('log-printer',option,val)

            #Set printer-specific options:
            if parser.has_section(prt+'-printer'):
                newPrinter.setOptions(parser.items(prt+'-printer'))
            self.Printers[prt] = newPrinter

    def addObj(self,obj):
        """
        Adds the object to all its Printers:

        :param obj: An object which can be handled by the Printers.
        """

        for prt in self.Printers.values():
            prt.addObj(obj)

    def setOutPutFiles(self,filename,silent=False):
        """
        Set the basename for the output files. Each printer will
        use this file name appended of the respective extension
        (i.e. .py for a python printer, .smodels for a summary printer,...)

        :param filename: Input file name
        :param silent: dont comment removing old files
        """

        for printer in self.Printers.values():
            printer.setOutPutFile(filename,silent=silent)

    def flush(self):
        """
        Ask all printers to write the output and clear their cache.
        If the printers return anything other than None,
        we pass it on.
        """
        ret = {}
        for printerType,printer in self.Printers.items():
            ret[printerType] = printer.flush()
        return ret

class BasicPrinter(object):
    """
    Super class to handle the basic printing methods
    """

    def __init__(self, output, filename):
        self.name = "basic"
        self.time = time.time() # time stamps

        self.outputList = []
        self.filename = filename
        self.output = output
        self.printingOrder = []
        self.toPrint = []

        if filename and os.path.isfile(filename):
            logger.warning("Removing file %s" %filename)
            os.remove(filename)

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self,fn):
        self._filename=fn
        self.mkdir()

    def mkdir(self ):
        """ create directory to file, if necessary """
        if not self.filename:
            return
        dirname = os.path.dirname ( self.filename )
        if dirname != "" and not os.path.exists ( dirname ):
            os.makedirs(dirname)

    def setOptions(self,options):
        """
        Store the printer specific options to control the output of each printer.
        Each option is stored as a printer attribute.

        :param options: a list of (option,value) for the printer.
        """

        for opt,value in options:
            setattr(self,opt,eval(value))

    def addObj(self,obj):
        """
        Adds object to the Printer.

        :param obj: A object to be printed. Must match one of the types defined in formatObj

        :return: True if the object has been added to the output. If the object does not belong
                to the pre-defined printing list toPrint, returns False.
        """

        for iobj,objType in enumerate(self.printingOrder):
            if isinstance(obj,objType):
                self.toPrint[iobj] = obj
                return True
        return False

    def openOutFile(self, filename, mode ):
        """ creates and opens a data sink,
            creates path if needed """
        d = os.path.dirname ( filename )
        if not os.path.exists ( d ):
            os.makedirs ( d )
            logger.info ( "creating directory %s" % d )
        return open ( filename, mode )


    def flush(self):
        """
        Format the objects added to the output, print them to the screen
        or file and remove them from the printer.
        """
        ret=""

        for obj in self.toPrint:
            if obj is None: continue
            output = self._formatObj(obj)
            if not output: continue  #Skip empty output
            ret += output
            if self.output == 'stdout':
                sys.stdout.write(output)
            elif self.output == 'file':
                if not self.filename:
                    logger.error('Filename not defined for printer')
                    return False
                with self.openOutFile(self.filename, "a") as outfile:
                    outfile.write(output)
                    outfile.close()

        self.toPrint = [None]*len(self.printingOrder)  #Reset printing objects
        self.time = time.time() ## prepare next timestamp
        return ret

    def _formatObj(self,obj):
        """
        Method for formatting the output depending on the type of object
        and output.

        :param obj: A object to be printed. Must match one of the types defined in formatObj

        """

        typeStr = type(obj).__name__
        try:
            formatFunction = getattr(self,'_format'+typeStr)
            return formatFunction(obj)
        except AttributeError as e:
            logger.debug('Error formating object %s: \n %s' %(typeStr,e))
            return False

class TxTPrinter(BasicPrinter):
    """
    Printer class to handle the printing of one single text output
    """
    def __init__(self, output = 'stdout', filename = None):
        BasicPrinter.__init__(self, output, filename)
        self.name = "log"
        self.printtimespent = False
        self.printingOrder = [OutputStatus,ExpResultList,TopologyList,
                             TheoryPredictionList,Uncovered]
        self.toPrint = [None]*len(self.printingOrder)

    def setOutPutFile(self,filename,overwrite=True,silent=False):
        """
        Set the basename for the text printer. The output filename will be
        filename.log.

        :param filename: Base filename
        :param overwrite: If True and the file already exists, it will be removed.
        :param silent: dont comment removing old files
        """

        self.filename = filename +'.' + self.name
        if overwrite and os.path.isfile(self.filename):
            if not silent:
                logger.warning("Removing old output file " + self.filename)
            os.remove(self.filename)

    def _formatDoc(self,obj):

        return False

    def _formatOutputStatus(self, obj):
        """
        Format data for a OutputStatus object.

        :param obj: A OutputStatus object to be printed.
        """

        output = ""
        output += "Input status: " + str(obj.filestatus) + "\n"
        # hidden feature, printtimespent, turn on in ini file, e.g.
        # [summary-printer] printtimespent = True
        if self.printtimespent:
            output += "Time spent: %.2fs\n" % ( time.time() - self.time )
        output += "Decomposition output status: " + str(obj.status) + " "
        st = "unknown status"
        if obj.status in obj.statusStrings:
            st = obj.statusStrings[obj.status]
        output += st + "\n"
        if obj.filestatus < 0: output += str(obj.warnings) + "\n"
        output += "# Input File: " + obj.inputfile + "\n"
        labels = list ( obj.parameters.keys() )
        labels.sort()
        # for label, par in obj.parameters.items():
        for label in labels:
            par=obj.parameters[label]
            output += "# " + label + " = " + str(par) + '\n'
        if obj.databaseVersion:
            output += "# Database version: %s\n" % obj.databaseVersion
        output += "=" * 80 + "\n"
        return output


    def _formatTopologyList(self, obj):
        """
        Format data for a TopologyList object.

        :param obj: A TopologyList object to be printed.
        """

        if not hasattr(self,'printdecomp') or not self.printdecomp:
            return None

        old_vertices = ""
        slabel = "Topologies Table"
        output = ""
        output += "  " + "="*56+ "  \n"
        output += "||" + " "*56+ "||\n"
        xspace = int((56-len(slabel))/2.)
        output += "||" + " "*xspace+slabel+" "*(56-xspace-len(slabel))+"||\n"
        output += "||" + " "*56+ "||\n"
        output += "  " + "="*56+ "  \n"

        for topo in obj:
            if old_vertices == str(topo.vertnumb):
                output += "\t .................................................. \n"
            else:
                output += "===================================================== \n"
                output += "Topology:\n"
                output += "Number of vertices: " + str(topo.vertnumb) + ' \n'
                old_vertices = str(topo.vertnumb)
            output += "Number of vertex parts: " + str(topo.vertparts) + '\n'
            totxsec = topo.getTotalWeight()
            output += "Total Global topology weight :\n" + totxsec.niceStr() + '\n'
            output += "Total Number of Elements: " + str(len(topo.elementList)) + '\n'
            if not hasattr(self,'addelementinfo') or not self.addelementinfo: continue
            for el in topo.elementList:
                output += "\t\t "+ 73 * "." + "\n"
                output += "\t\t Element: \n"
                output += self._formatElement(el) + "\n"

        return output


    def _formatElement(self, obj):
        """
        Format data for a Element object.

        :param obj: A Element object to be printed.
        """

        output = ""
        output +="\t\t Element ID: " + str(obj.elID)
        output += "\n"
        output += "\t\t Particles in element: " + str(obj.evenParticles)
        output += "\n"
        output += "\t\t Final states in element: " + str(obj.getFinalStates())
        output += "\n"
        output += "\t\t The element masses are \n"
        for i, mass in enumerate(obj.mass):
            output += "\t\t Branch %i: " % i + str(mass) + "\n"
        output += "\n"
        output += "\t\t The element PIDs are \n"
        for pidlist in obj.pdg:
            output += "\t\t PIDs: "+ str(pidlist) + "\n"
        output += "\t\t The element weights are: \n \t\t " + obj.weight.niceStr().replace("\n", "\n \t\t ")

        return output


    def _formatExpResultList(self, obj):
        """
        Format data for a ExpResultList object.

        :param obj: A ExpResultList object to be printed.
        """

        if not hasattr(self,"printdatabase") or not self.printdatabase:
            return None

        slabel = "Selected Experimental Results"
        output = ""
        output += "  " + "="*56+ "  \n"
        output += "||" + " "*56+ "||\n"
        xspace = int((56-len(slabel))/2.)
        output += "||" + " "*xspace+slabel+" "*(56-xspace-len(slabel))+"||\n"
        output += "||" + " "*56+ "||\n"
        output += "  " + "="*56+ "  \n"

        for expRes in obj.expResultList:
            output += self._formatExpResult(expRes)

        return output+"\n"


    def _formatExpResult(self, obj):
        """
        Format data for a ExpResult object.

        :param obj: A ExpResult object to be printed.
        """

        txnames = []
        for dataset in obj.datasets:
            for txname in dataset.txnameList:
                tx = txname.txName
                if not tx in txnames:
                    txnames.append(tx)

        txnames = sorted(txnames)
        output = ""
        output += "========================================================\n"
        output += "Experimental Result ID: " + obj.globalInfo.id + '\n'
        output += "Tx Labels: " + str(txnames) + '\n'
        output += "Sqrts: %2.2E\n" % obj.globalInfo.sqrts.asNumber(TeV)
        if hasattr(self,"addanainfo") and self.addanainfo:
            output += "\t -----------------------------\n"
            output += "\t Elements tested by analysis:\n"
            listOfelements = []
            for dataset in obj.datasets:
                for txname in dataset.txnameList:
                    for el in txname._topologyList.getElements():
                        if not el.toStr() in listOfelements: listOfelements.append(el.toStr())
            for el in listOfelements:
                output += "\t    " + str(el) + "\n"

        return output


    def _formatTheoryPredictionList(self, obj):
        """
        Format data for a TheoryPredictionList object.

        :param obj: A TheoryPredictionList object to be printed.
        """
        slabel = "Theory Predictions and"
        output = ""
        output += "  " + "="*56+ "  \n"
        output += "||" + " "*56+ "||\n"
        xspace = int((56-len(slabel))/2.)
        output += "||" + " "*xspace+slabel+" "*(56-xspace-len(slabel))+"||\n"
        slabel = "Experimental Constraints"
        xspace = int((56-len(slabel))/2.)
        output += "||" + " "*xspace+slabel+" "*(56-xspace-len(slabel))+"||\n"
        output += "||" + " "*56+ "||\n"
        output += "  " + "="*56+ "  \n"


        for theoryPrediction in obj._theoryPredictions:
            expRes = theoryPrediction.expResult
            dataId = theoryPrediction.dataId()
            txnames = [str(txname) for txname in theoryPrediction.txnames]
            txnames = sorted(list(set(txnames)))
            output += "\n"
            output += "---------------Analysis Label = " + expRes.globalInfo.id + "\n"
            output += "-------------------Dataset Label = " + str(dataId).replace("None","(UL)") + "\n"
            output += "-------------------Txname Labels = " + str(txnames) + "\n"
            output += "Analysis sqrts: " + str(expRes.globalInfo.sqrts) + \
                    "\n"

            output += "Theory prediction: " + str(theoryPrediction.xsection.value) + "\n"
            output += "Theory conditions:"
            if not theoryPrediction.conditions:
                output += "  " + str(theoryPrediction.conditions) + "\n"
            else:
                condlist = []
                for cond in theoryPrediction.conditions:
                    condlist.append(theoryPrediction.conditions[cond])
                output += str(condlist) + "\n"

            #Get upper limit for the respective prediction:
            upperLimit = theoryPrediction.getUpperLimit(expected=False)
            upperLimitExp = theoryPrediction.getUpperLimit(expected=True)

            output += "Observed experimental limit: " + str(upperLimit) + "\n"
            if not upperLimitExp is None:
                output += "Expected experimental limit: " + str(upperLimitExp) + "\n"
            output += "Observed r-Value: %s\n" %theoryPrediction.getRValue(expected=False)
            if not upperLimitExp is None:
                output += "Expected r-Value: %s\n" %theoryPrediction.getRValue(expected=True)
            if hasattr(theoryPrediction,'chi2') and not theoryPrediction.chi2 is None:
                output += "Chi2: " + str(theoryPrediction.chi2) + "\n"
                output += "Likelihood: " + str(theoryPrediction.likelihood) + "\n"

            if hasattr(self,"printextendedresults") and self.printextendedresults:
                if theoryPrediction.mass:
                    for ibr, br in enumerate(theoryPrediction.mass):
                        output += "Masses in branch %i: " % ibr + str(br) + "\n"
                IDList = list(set([el.elID for el in theoryPrediction.elements]))
                if IDList:
                    output += "Contributing elements: " + str(IDList) + "\n"
                for pidList in theoryPrediction.PIDs:
                    output += "PIDs:" + str(pidList) + "\n"

        return output


    def _formatUncovered(self, obj):
        """
        Format all uncovered data.

        :param obj: Uncovered object to be printed.
        """

        nprint = 10  # Number of missing topologies to be printed (ordered by cross sections)

        #First sort groups by label
        groups = sorted(obj.groups[:], key = lambda g: g.label)
        #Get summary of groups:
        output = "\n"
        for group in groups:
            output += "Total cross-section for %s (fb): %10.3E\n" %(group.description,group.getTotalXSec())

        output += "\nFull information on unconstrained cross sections\n"
        output += "================================================================================\n"

        #Get detailed information:
        for group in groups:
            description = group.description
            sqrts = group.sqrts.asNumber(TeV)
            if not group.generalElements:
                output += "No %s found\n" %description
                output += "================================================================================\n"
                continue
            output += "%s with the highest cross sections (up to %i):\n" %(description,nprint)
            output += "Sqrts (TeV)   Weight (fb)                  Element description\n"
            for genEl in group.generalElements[:nprint]:
                output += "%5s         %10.3E    # %53s\n" % (str(sqrts),genEl.missingX, genEl)
                if hasattr(self, "addcoverageid") and self.addcoverageid:
                    contributing = []
                    for el in genEl._contributingElements:
                        contributing.append(el.elID)
                    output += "Contributing elements %s\n" % str(contributing)
            output += "================================================================================\n"
        return output

class SummaryPrinter(TxTPrinter):
    """
    Printer class to handle the printing of one single summary output.
    It uses the facilities of the TxTPrinter.
    """

    def __init__(self, output = 'stdout', filename = None):
        TxTPrinter.__init__(self, output, filename)
        self.name = "summary"
        self.printingOrder = [OutputStatus,TheoryPredictionList, Uncovered]
        self.toPrint = [None]*len(self.printingOrder)

    def setOutPutFile(self,filename,overwrite=True,silent=False):
        """
        Set the basename for the text printer. The output filename will be
        filename.smodels.
        :param filename: Base filename
        :param overwrite: If True and the file already exists, it will be removed.
        :param silent: dont comment removing old files
        """

        self.filename = filename +'.smodels'
        if overwrite and os.path.isfile(self.filename):
            if not silent:
                logger.warning("Removing old output file " + self.filename)
            os.remove(self.filename)

    def _formatTheoryPredictionList(self, obj):
        """
        Format data of the TheoryPredictionList object.

        :param obj: A TheoryPredictionList object to be printed.
        """
        obj.sortTheoryPredictions()
        if hasattr(self,"expandedsummary") and not self.expandedsummary:
            theoPredictions = [obj._theoryPredictions[0]]
        else:
            theoPredictions = obj._theoryPredictions

        output = ""

        rvalues = []
        output += "#Analysis  Sqrts  Cond_Violation  Theory_Value(fb)  Exp_limit(fb)  r  r_expected"
        output += "\n\n"
        for theoPred in theoPredictions:
            expResult = theoPred.expResult
            txnames = theoPred.txnames
            ul = theoPred.getUpperLimit(expected=False)
            signalRegion = theoPred.dataset.getID()
            if signalRegion is None:
                signalRegion = '(UL)'
            value = theoPred.xsection.value
            r = theoPred.getRValue(expected=False)
            r_expected = theoPred.getRValue(expected=True)
            rvalues.append(r)

            output += "%19s  " % (expResult.globalInfo.id)  # ana
            # output += "%4s " % (expResult.globalInfo.sqrts/ TeV)  # sqrts
            output += "%2.2E  " % (expResult.globalInfo.sqrts.asNumber(TeV))  # sqrts
            output += "%5s " % theoPred.getmaxCondition()  # condition violation
            output += "%10.3E %10.3E " % (value.asNumber(fb), ul.asNumber(fb))  # theory cross section , expt upper limit
            if r_expected: output += "%10.3E %10.3E" % (r, r_expected)
            else: output += "%10.3E  N/A" %r
            output += "\n"
            output += " Signal Region:  "+signalRegion+"\n"
            txnameStr = str(sorted(list(set([str(tx) for tx in txnames]))))
            txnameStr = txnameStr.replace("'","").replace("[", "").replace("]","")
            output += " Txnames:  " + txnameStr + "\n"
            if hasattr(theoPred,'chi2') and not theoPred.chi2 is None:
                output += " Chi2, Likelihood = %10.3E %10.3E\n" % (theoPred.chi2, theoPred.likelihood)

            if not (theoPred is obj[-1]):
                output += 80 * "-"+ "\n"

        output += "\n \n"
        output += 80 * "=" + "\n"
        output += "The highest r value is = %.12f\n" % max(rvalues)
        # output += "The highest r value is = " + str(max(rvalues)) + "\n"

        return output

class PyPrinter(BasicPrinter):
    """
    Printer class to handle the printing of one single pythonic output
    """

    def __init__(self, output = 'stdout', filename = None):
        BasicPrinter.__init__(self, output, filename)
        self.name = "py"
        self.printtimespent = False
        self.printingOrder = [OutputStatus,TopologyList,TheoryPredictionList,Uncovered]
        self.toPrint = [None]*len(self.printingOrder)

    def setOutPutFile(self,filename,overwrite=True,silent=False):
        """
        Set the basename for the text printer. The output filename will be
        filename.py.
        :param filename: Base filename
        :param overwrite: If True and the file already exists, it will be removed.
        :param silent: dont comment removing old files
        """

        self.filename = filename +'.py'
        if overwrite and os.path.isfile(self.filename):
            if not silent:
                logger.warning("Removing old output file " + self.filename)
            os.remove(self.filename)

    def flush(self):
        """
        Write the python dictionaries generated by the object formatting
        to the defined output
        """

        outputDict = {}
        for obj in self.toPrint:
            if obj is None: continue
            output = self._formatObj(obj)
            if not output: continue  #Skip empty output
            outputDict.update(output)

        output = 'smodelsOutput = '+str(outputDict)
        if self.output == 'stdout':
            sys.stdout.write(output)
        elif self.output == 'file':
            if not self.filename:
                logger.error('Filename not defined for printer')
                return False
            with open(self.filename, "a") as outfile:
                outfile.write(output)
                outfile.close()

        self.toPrint = [None]*len(self.printingOrder)
        ## it is a special feature of the python printer
        ## that we also return the output dictionary
        return outputDict

    def _formatTopologyList(self, obj):
        """
        Format data for a TopologyList object.

        :param obj: A TopologyList object to be printed.
        """

        if not hasattr(self,'addelementlist') or not self.addelementlist:
            return None

        elements = []

        for topo in obj:
            for el in topo.elementList:
                thisEl = self._formatElement(el)
                if thisEl: elements.append(thisEl)


        return {"Element": elements}

    def _formatElement(self, obj):
        """
        Format data for a Element object.

        :param obj: A Element object to be printed.
        """

        elDic = {}
        elDic["ID"] = obj.elID
        elDic["Particles"] = str(obj.evenParticles)
        elDic["Masses (GeV)"] = [[round(m.asNumber(GeV),2) for m in br] for br in obj.mass]
        elDic["PIDs"] = obj.pdg
        elDic["Weights (fb)"] = {}
        elDic["final states"] = [str(fs) for fs in obj.getFinalStates()]
        sqrts = [info.sqrts.asNumber(TeV) for info in obj.weight.getInfo()]
        allsqrts = sorted(list(set(sqrts)))
        for ssqrts in allsqrts:
            sqrts = ssqrts * TeV
            xsecs = [xsec.value.asNumber(fb) for xsec in obj.weight.getXsecsFor(sqrts)]
            if len(xsecs) != 1:
                logger.warning("Element cross sections contain multiple values for %s .\
                Only the first cross section will be printed" %str(sqrts))
            xsecs = xsecs[0]
            sqrtsStr = 'xsec '+str(sqrts.asNumber(TeV))+' TeV'
            elDic["Weights (fb)"][sqrtsStr] = xsecs
        return elDic

    def _formatOutputStatus(self, obj):
        """
        Format data for a OutputStatus object.

        :param obj: A OutputStatus object to be printed.
        """

        infoDict = {}
        for key,val in obj.parameters.items():
            try:
                infoDict[key] = eval(val)
            except (NameError,TypeError):
                infoDict[key] = val
        infoDict['file status'] = obj.filestatus
        infoDict['decomposition status'] = obj.status
        infoDict['warnings'] = obj.warnings
        infoDict['input file'] = obj.inputfile
        infoDict['database version'] = obj.databaseVersion
        infoDict['smodels version'] = obj.smodelsVersion
        # hidden feature, printtimespent, turn on in ini file, e.g.
        # [summary-printer] printtimespent = True
        if self.printtimespent:
            infoDict['time spent'] =  "%.2fs" %(time.time() - self.time)
        return {'OutputStatus' : infoDict}

    def _formatTheoryPredictionList(self, obj):
        """
        Format data of the TheoryPredictionList object.

        :param obj: A TheoryPredictionList object to be printed.
        """
        obj.sortTheoryPredictions()
        ExptRes = []
        for theoryPrediction in obj._theoryPredictions:
            expResult = theoryPrediction.expResult
            expID = expResult.globalInfo.id
            datasetID = theoryPrediction.dataId()
            dataType = theoryPrediction.dataType()
            ul = theoryPrediction.getUpperLimit()
            ulExpected = theoryPrediction.getUpperLimit(expected = True)
            if isinstance(ul,unum.Unum):
                ul = ul.asNumber(fb)
            if isinstance(ulExpected,unum.Unum):
                ulExpected = ulExpected.asNumber(fb)

            value = theoryPrediction.xsection.value.asNumber(fb)
            txnamesDict = {}
            for el in theoryPrediction.elements:
                if not el.txname.txName in txnamesDict:
                    txnamesDict[el.txname.txName] = el.weight[0].value.asNumber(fb)
                else:
                    txnamesDict[el.txname.txName] += el.weight[0].value.asNumber(fb)
            maxconds = theoryPrediction.getmaxCondition()
            if theoryPrediction.mass  is None:
                mass = None
            else:
                mass = np.array(theoryPrediction.mass,dtype=object)

            #Add width information to the mass array:
            totalwidth = theoryPrediction.totalwidth

            def _convWidth ( x ):
                if type(x) == type(GeV):
                    x=float(x.asNumber(GeV))
                if x == float("inf"):
                    x="prompt"
                if x == 0.:
                    x="stable"
                return x
            widths = None
            if totalwidth is not None:
                widths = [ [_convWidth(x) for x in br] for br in totalwidth ]

            def roundme ( x ):
                if type(x)==tuple:
                    return ( round(x[0].asNumber(GeV),2), x[1].asNumber(GeV) )
                return round(x.asNumber(GeV),2)

            if mass is not None:
                mass = [[roundme(m) for m in mbr] for mbr in mass]

            sqrts = expResult.globalInfo.sqrts

            r = theoryPrediction.getRValue(expected=False)
            r_expected = theoryPrediction.getRValue(expected=True)

            resDict = {'maxcond': maxconds, 'theory prediction (fb)': value,
                        'upper limit (fb)': ul,
                        'expected upper limit (fb)': ulExpected,
                        'TxNames': sorted(txnamesDict.keys()),
                        'Mass (GeV)': mass,
                        'AnalysisID': expID,
                        'DataSetID' : datasetID,
                        'AnalysisSqrts (TeV)': sqrts.asNumber(TeV),
                        'lumi (fb-1)' : (expResult.globalInfo.lumi*fb).asNumber(),
                        'dataType' : dataType,
                        'r' : r, 'r_expected' : r_expected}
            if widths:
                resDict["Width (GeV)"] = widths
            if hasattr(self,"addtxweights") and self.addtxweights:
                resDict['TxNames weights (fb)'] =  txnamesDict
            if hasattr(theoryPrediction,'chi2') and not theoryPrediction.chi2 is None:
                resDict['chi2'] = theoryPrediction.chi2
                resDict['likelihood'] = theoryPrediction.likelihood
            ExptRes.append(resDict)


        return {'ExptRes' : ExptRes}

    def _formatDoc(self, obj):
        """
        Format a pyslha object to be printed as a dictionary

        :param obj: pyslha object
        """

        MINPAR = dict(obj.blocks['MINPAR'].entries)
        EXTPAR = dict(obj.blocks['EXTPAR'].entries)
        mass = OrderedDict(obj.blocks['MASS'].entries.items())
        chimix = {}
        for key in obj.blocks['NMIX'].entries:
            val = obj.blocks['NMIX'].entries[key]
            if key[0] != 1: continue
            newkey = 'N'+str(key[0])+str(key[1])
            chimix[newkey] = val
        chamix = {}
        for key in obj.blocks['UMIX'].entries:
            val = obj.blocks['UMIX'].entries[key]
            newkey = 'U'+str(key[0])+str(key[1])
            chamix[newkey] = val
        for key in obj.blocks['VMIX'].entries:
            val = obj.blocks['VMIX'].entries[key]
            newkey = 'V'+str(key[0])+str(key[1])
            chamix[newkey] = val
        stopmix = {}
        for key in obj.blocks['STOPMIX'].entries:
            val = obj.blocks['STOPMIX'].entries[key]
            newkey = 'ST'+str(key[0])+str(key[1])
            stopmix[newkey] = val
        sbotmix = {}
        for key in obj.blocks['SBOTMIX'].entries:
            val = obj.blocks['SBOTMIX'].entries[key]
            newkey = 'SB'+str(key[0])+str(key[1])
            sbotmix[newkey] = val

        return {'MINPAR' : MINPAR, 'chimix' : chimix, 'stopmix' : stopmix,
                'chamix' : chamix, 'MM' : {}, 'sbotmix' : sbotmix,
                'EXTPAR' : EXTPAR, 'mass' : mass}

    def _formatUncovered(self, obj):
        """
        Format data of the Uncovered object containing coverage info

        :param obj: An Uncovered object to be printed.
        """

        nprint = 10  # Number of missing topologies to be printed (ordered by cross sections)

        uncoveredDict = {}
        #First sort groups by label
        groups = sorted(obj.groups[:], key = lambda g: g.label)
        #Add summary of groups:
        for group in groups:
            sqrts = group.sqrts.asNumber(TeV)
            uncoveredDict["Total xsec for %s (fb)" %group.description] = group.getTotalXSec()
            uncoveredDict["%s" %group.description] = []
            for genEl in group.generalElements[:nprint]:
                genElDict = {'sqrts (TeV)' : sqrts, 'weight (fb)' : genEl.missingX,
                                'element' : str(genEl)}
                if hasattr(self,"addelementlist") and self.addelementlist:
                    genElDict["element IDs"] = [el.elID for el in genEl._contributingElements]
                uncoveredDict["%s" %group.description].append(genElDict)

        return uncoveredDict

class XmlPrinter(PyPrinter):
    """
    Printer class to handle the printing of one single XML output
    """
    def __init__(self, output = 'stdout', filename = None):
        PyPrinter.__init__(self, output, filename)
        self.name = "xml"
        self.printingOrder = [OutputStatus,TopologyList,TheoryPredictionList,Uncovered]
        self.toPrint = [None]*len(self.printingOrder)


    def setOutPutFile(self,filename,overwrite=True,silent=False):
        """
        Set the basename for the text printer. The output filename will be
        filename.xml.
        :param filename: Base filename
        :param overwrite: If True and the file already exists, it will be removed.
        :param silent: dont comment removing old files
        """

        self.filename = filename +'.xml'
        if overwrite and os.path.isfile(self.filename):
            if not silent:
                logger.warning("Removing old output file " + self.filename)
            os.remove(self.filename)


    def convertToElement(self,pyObj,parent,tag=""):
        """
        Convert a python object (list,dict,string,...)
        to a nested XML element tree.
        :param pyObj: python object (list,dict,string...)
        :param parent: XML Element parent
        :param tag: tag for the daughter element
        """

        tag = tag.replace(" ","_").replace("(","").replace(")","")
        if not isinstance(pyObj,list) and not isinstance(pyObj,dict):
            parent.text = str(pyObj).lstrip().rstrip()
        elif isinstance(pyObj,dict):
            for key,val in sorted(pyObj.items()):
                key = key.replace(" ","_").replace("(","").replace(")","")
                newElement = ElementTree.Element(key)
                self.convertToElement(val,newElement,tag=key)
                parent.append(newElement)
        elif isinstance(pyObj,list):
            parent.tag += '_List'
            for val in pyObj:
                newElement = ElementTree.Element(tag)
                self.convertToElement(val,newElement,tag)
                parent.append(newElement)


    def flush(self):
        """
        Get the python dictionaries generated by the object formatting
        to the defined output and convert to XML
        """

        outputDict = {}
        for obj in self.toPrint:
            if obj is None: continue
            output = self._formatObj(obj)  # Convert to python dictionaries
            if not output: continue  #Skip empty output
            outputDict.update(output)

        root = None
        #Convert from python dictionaries to xml:
        if outputDict:
            root = ElementTree.Element('smodelsOutput')
            self.convertToElement(outputDict,root)
            rough_xml = ElementTree.tostring(root, 'utf-8')
            nice_xml = minidom.parseString(rough_xml).toprettyxml(indent="    ")
            if self.output == 'stdout':
                sys.stdout.write(nice_xml)
            elif self.output == 'file':
                if not self.filename:
                    logger.error('Filename not defined for printer')
                    return False
                with open(self.filename, "a") as outfile:
                    outfile.write(nice_xml)
                    outfile.close()

        self.toPrint = [None]*len(self.printingOrder)
        return root

class SLHAPrinter(TxTPrinter):
    """
    Printer class to handle the printing of slha format summary output.
    It uses the facilities of the TxTPrinter.
    """

    def __init__(self, output = 'file', filename = None):
        TxTPrinter.__init__(self, output, filename)
        self.name = "slha"
        self.docompress = 0
        self.combinesr = 0
        self.printingOrder = [OutputStatus,TheoryPredictionList, Uncovered]
        self.toPrint = [None]*len(self.printingOrder)

    def setOutPutFile(self,filename,overwrite=True,silent=False):
        """
        Set the basename for the text printer. The output filename will be
        filename.smodels.
        :param filename: Base filename
        :param overwrite: If True and the file already exists, it will be removed.
        :param silent: dont comment removing old files
        """

        self.filename = filename +'.smodelsslha'
        if overwrite and os.path.isfile(self.filename):
            if not silent:
                logger.warning("Removing old output file " + self.filename)
            os.remove(self.filename)

    def _formatOutputStatus(self, obj):

        smodelsversion = obj.smodelsVersion
        if not smodelsversion.startswith("v"): smodelsversion = "v" + smodelsversion
        output = "BLOCK SModelS_Settings\n"
        output += " 0 %-25s #SModelS version\n" %(smodelsversion)
        output += " 1 %-25s #database version\n" %(obj.databaseVersion.replace(" ",""))
        output += " 2 %-25s #maximum condition violation\n" % (obj.parameters['maxcond'])
        output += " 3 %-25s #compression (0 off, 1 on)\n" % (self.docompress)
        output += " 4 %-25s #minimum mass gap for mass compression [GeV]\n" % (obj.parameters['minmassgap'])
        output += " 5 %-25s #sigmacut [fb]\n" % (obj.parameters['sigmacut'])
        output += " 6 %-25s #signal region combination (0 off, 1 on)\n\n" %(self.combinesr)

        #for SLHA output we always want to have SModelS_Exclusion block, if no results we write it here
        if obj.status <=0:
            output += "BLOCK SModelS_Exclusion\n"
            output += " 0 0 %-30s #output status (-1 not tested, 0 not excluded, 1 excluded)\n\n" % (-1)

        return output

    def _formatTheoryPredictionList(self, obj):
        output = "BLOCK SModelS_Exclusion\n"
        if not obj._theoryPredictions[0]:
            excluded = -1
        else:
            obj.sortTheoryPredictions()
            firstResult = obj._theoryPredictions[0]
            r = firstResult.getRValue()
            if r > 1: excluded = 1
            else: excluded = 0
        output += " 0 0 %-30s #output status (-1 not tested, 0 not excluded, 1 excluded)\n" % (excluded)
        if excluded == 0: rList = [firstResult]
        elif excluded == 1: rList = obj._theoryPredictions
        else: rList = []
        cter = 1
        for theoPred in rList:
            expResult = theoPred.expResult
            txnames = theoPred.txnames
            signalRegion  = theoPred.dataId()
            if signalRegion is None:
                signalRegion = '(UL)'
            r = theoPred.getRValue()
            r_expected = theoPred.getRValue( expected=True )
            txnameStr = str(sorted(list(set([str(tx) for tx in txnames]))))
            txnameStr = txnameStr.replace("'","").replace("[", "").replace("]","")

            if r <1 and not excluded == 0: break
            output += " %d 0 %-30s #txname \n" % (cter, txnameStr )
            output += " %d 1 %-30.3E #r value\n" % (cter, r)
            if not r_expected: output += " %d 2 N/A                            #expected r value\n" % (cter)
            else: output += " %d 2 %-30.3E #expected r value\n" % (cter, r_expected)
            output += " %d 3 %-30.2f #condition violation\n" % (cter, theoPred.getmaxCondition())
            output += " %d 4 %-30s #analysis\n" % (cter, expResult.globalInfo.id)
            output += " %d 5 %-30s #signal region \n" %(cter, signalRegion.replace(" ","_"))
            if hasattr(theoPred,'chi2') and not theoPred.chi2 is None:
                output += " %d 6 %-30.3E #Chi2\n" % (cter, theoPred.chi2)
                output += " %d 7 %-30.3E #Likelihood\n" % (cter, theoPred.likelihood)
            else:
                output += " %d 6 N/A                            #Chi2\n" % (cter)
                output += " %d 7 N/A                            #Likelihood\n" % (cter)
            output += "\n"
            cter += 1
        return output

    def _formatUncovered(self, obj):

        #First sort groups by label
        groups = sorted(obj.groups[:], key = lambda g: g.label)
        #Get summary of groups:
        output = "\nBLOCK SModelS_Coverage"
        for i,group in enumerate(sorted(groups, key = lambda g: g.label)):
            output += "\n %d 0 %-30s      # %s" %(i,group.label,group.description)
            output += "\n %d 1 %-30.3E      # %s" %(i,group.getTotalXSec(),"Total cross-section (fb)")
        output += "\n"
        return output
