"""
.. module:: printer
   :synopsis: Facility used in classes to derive from and be able to print
              different data types in different forms.

.. moduleauthor:: Wolfgang Magerl <wolfgang.magerl@gmail.com>
"""

from __future__ import print_function
import logging

logger = logging.getLogger(__name__)


class Printer(object):
    """
    Printer class.
    
    """
    def __init__(self):
        self.output = None


    def printout(self, target="stdout"):
        """
        Print the content of the data structure to the target.

        :param target: The target to print to. Possible values: stdout, html.
                       Default: stdout.
        :returns: None
        
        """
        # Branch, Element, Topology, TopologyList, Analysis, AnalysisList,
        # Cluster
        self.output = self.formatData()

        if target == "stdout":
            print(self.output)
        elif target == "file":
            pass


    def formatData(self):
        """
        Format data of the derived object.
        
        Has to be implemented in the derived object. The real implementation is
        selected through dynamic binding.
        
        :raises: NotImplementedError  
              
        """
        raise NotImplementedError


    def formatTopologyListData(self):
        """
        Format data of a TopologyList object.
        
        """

        from smodels.tools import smsPrettyPrinter
        from smodels.tools.physicsUnits import fb
        #from prettytable import PrettyTable
        output = "\n"
        output += "Number of Global topologies = " + str(len(self)) + "\n\n"

        printer = smsPrettyPrinter.SmsPrettyPrinter()
        #evTopTable = PrettyTable(["Topology", "#Vertices", "#Insertions",
        #                          "#Elements", "Sum of weights"])
        output += "  # #vrtces #insertions        #els   #sum(weights) [fb]\n"
        # evElementTable = PrettyTable(["Topology", "Element", "Particles B[0]",
        #                              "Particles B[1]", "Masses B[0]",
        #                              "Masses B[1]", "Element Weight"])

        eltot = 0
        # totweight = []
        # Print Results:
        # for i in range(len(SMSTopList)):
        for i, topo in enumerate(self):
            sumw = topo.getTotalWeight().getDictionary()
            #evTopTable.add_row([i, topo.vertnumb, topo.vertparts,
            #                    len(topo.elementList),
            #                    smsPrettyPrinter.wrap(printer.pformat(sumw),
            #                                          width=22)])
            vn=str(topo.vertnumb).replace(" ","") 
            vp=str(topo.vertparts).replace(" ","") 
            ne=len(topo.elementList)
            output+="%3d  %-5s  %-18s %3d   " % (i, vn, vp, ne )
            # sw=smsPrettyPrinter.wrap(printer.pformat(sumw),width=22)
            for (key,value) in sumw.items():
                skey=key.replace(" [TeV]","")
                svalue=float ( value / fb )
                output+="%2d TeV: %6.2f " % ( int(float(skey)), svalue )
               # output+="\n key %s value %s \n" % ( key,value)
            output+="\n"
            eltot += len(topo.elementList)

        # Print element list for Topology[i]:
            if i == 0:
                for j, el in enumerate(topo.elementList):
                    if el.getParticles() != [[['b', 'b']], [['b', 'b']]]:
                        continue
                    m1 = printer.pformat(el.getMasses()[0])
                    m2 = printer.pformat(el.getMasses()[1])
                    dc = printer.pformat(el.weight.getDictionary())
                    row = [i, j, el.getParticles()[0], el.getParticles()[1],
                           smsPrettyPrinter.wrap(m1, width=25),
                           smsPrettyPrinter.wrap(m2, width=25),
                           smsPrettyPrinter.wrap(dc, width=25)]
        #            evElementTable.add_row(row)
        #        evElementTable.add_row(["---", "---", "---", "---", "---",
        #                                "---", "---"])

        #output += str(evTopTable) + "\n\n"
        output += "Total Number of Elements = " + str(eltot) + "\n"
        output += "Total weight = " + str(self.getTotalWeight()) + "\n"
        # output += evElementTable + "\n"

        return output


    def formatTheoryPredictionData(self):
        """
        Format data of a TheoryPrediction object.
        
        """
        output = ""

        for theoryPrediction in self:
            output += "\n"
            output += "analysis: " + str(theoryPrediction.analysis) + "\n"
            output += "mass: " + str(theoryPrediction.mass) + "\n"
            output += "theory prediction: " + str(theoryPrediction.value) + \
                      "\n"
            output += "theory conditions:\n"
            if not theoryPrediction.conditions:
                output += "  " + str(theoryPrediction.conditions) + "\n"
            else:
                for cond in theoryPrediction.conditions:
                    output += "  " + str(theoryPrediction.conditions[cond]) + \
                              "\n"
            experimentalLimit = theoryPrediction.analysis.getUpperLimitFor(
                    theoryPrediction.mass)
            output += "experimental limit: " + str(experimentalLimit) + "\n"

        return output

    def formatStatusData(self):
        """
        Format data of the output status object.
        """
        output = ""

        output += "SLHA status: " + str(self.slhastatus) + "\n"
        output += "Decomposition output status: "+str(self.status)+" "+self.statusStrings[self.status] + "\n" #FIXME where should status strings go?
        if self.slhastatus < 0: output += str(self.warnings) + "\n"
        output += "================================================================================\n"

        return output


    def formatResultsData(self):
        """
        Format data of the final output object.
        """
        output = ""

        if self.bestresultonly:
            output += "The result with highest R value is\n"
            self.outputarray = self.bestresult

        output += "#Analysis  Topology  Sqrts  Cond_Violation  Theory_Value(fb)  Exp_limit(fb)  r\n\n"
        for op in self.outputarray:
            output += "%19s %16s %4s %5s %10.3E %10.3E %10.3E\n"%(op.aname, op.topo, op.sqrts, op.cond, op.tval, op.exptval, op.rval)
            if self.describeTopo: output += "#" + str(op.topo_description) + "\n"
            if not op == self.outputarray[-1]: output += "--------------------------------------------------------------------------------\n"

        for op in self.bestresult:
            output += "\n \n"
            output += "================================================================================\n"
            output += "The highest R value is r_ratio = " + str(op.rval) + "\n"

        return output

    def formatSLHAData(self, maxcond):
        """
        Format data of the slha checks output object.
        """
        output = ""

        output += "Input file: " + self.filename + "\n"
        output += "Sigmacut: " + str(self.sigmacut) + "\n"
        output += "Minmassgap: " + str(self.massgap) + "\n"
        output += "Maxcond: " + str(maxcond) + "\n"
        output += "LSP PID, mass: " + str(self.findLSP(returnmass=True)) + "\n"
        output += "NLSP PID, mass: " + str(slhaStatus.findNLSP(returnmass=True)) + "\n"
        output += "================================================================================\n"

        return output

    def formatMissingData(self):
        """
        Format data of missing topology list.
        """
        output = ""

        output += "\n================================================================================\n"
        output += "Missing topologies with high cross sections:\n"
        output += "Sqrts (TeV)   Weight (fb)        Topology description\n"

        for topo in self.topos:
            output += "%5s %10.3E    # %45s" % (topo.sqrts, topo.weight, topo.topo) #FIXME need rmvunit, str() here?!

