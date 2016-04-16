#!/usr/bin/env python

"""
.. module:: theory.lheReader
   :synopsis: Provides a class that creates SMSEvents from LHE files.

.. moduleauthor:: Wolfgang Waltenberger <wolfgang.waltenberger@gmail.com>
.. moduleauthor:: Andre Lessa <lessa.a.p@gmail.com>

"""

import logging
from smodels.theory.auxiliaryFunctions import index_bisect
from smodels.theory.crossSection import XSectionList, XSection
from smodels.theory.vertex import Vertex
from smodels.tools.physicsUnits import TeV, pb, GeV
from smodels.particleDefinitions import useParticlesPidDict
from smodels.theory.exceptions import SModelSTheoryError as SModelSError

logger = logging.getLogger(__name__)

def getInputData(lhefile):
    """
    Get model information from LHE file.
    
    :returns: XSectionList and particles dictionary
    """
    
    try:
        reader = LheReader(lhefile)
    except:
        logger.info("The file %s cannot be parsed as a LHE file: %s" % (lhefile) )
        raise SModelSError()

    # Get cross-section from LHE file
    xSectionList = getXsecsFrom(reader, addEvents=False)
    # Only use the highest order cross-sections for each process
    xSectionList.removeLowerOrder()
    # Order xsections by PDGs to improve performance
    xSectionList.order()    
    # Add mass, width and decay information from SLHA file to the defined particles
    particlesDict = getParticleInfoFrom(reader,useParticlesPidDict)
    reader.close()
    
    return xSectionList,particlesDict

def getXsecsFrom(lheInput, addEvents=True):
    """
    Obtain cross-sections from input LHE file.
    
    :parameter lheInput: LHE input file with unweighted MC events or a LheReader object
    :parameter addEvents: if True, add cross-sections with the same mothers,
                      otherwise return the event weight for each pair of mothers
    :returns: a XSectionList object
    
    """
    
    if isinstance(lheInput,LheReader):
        reader = lheInput
        reader.reset()
    elif isinstance(lheInput,str):
        reader = LheReader(lheInput)
    else:
        logger.error("Wrong input format")
        raise SModelSError()
        
    # Store information about all cross-sections in the LHE file
    xSecsInFile = XSectionList()
    
    if not type ( reader.metainfo["totalxsec"] ) == type ( pb) :
        logger.error("Cross-section information not found in LHE file.")        
        raise SModelSError()
    elif not reader.metainfo["nevents"]:
        logger.error("Total number of events information not found in LHE " +
                     "file.")
        raise SModelSError()
    elif not type ( reader.metainfo["sqrts"] ) == type ( TeV ):
        logger.error("Center-of-mass energy information not found in LHE " +
                     "file.")
        raise SModelSError()

    # Common cross-section info
    totxsec = reader.metainfo["totalxsec"]
    nevts = reader.metainfo["nevents"]
    sqrtS = reader.metainfo["sqrts"]
    eventCs = totxsec / float(nevts)


    # Get all mom pids
    allpids = []
    for event in reader:
        allpids.append(tuple(sorted(event.getMom())))
    pids = set(allpids)
    # Generate zero cross-sections for all independent pids
    for pid in pids:
        xsec = XSection()
        xsec.info.sqrts = sqrtS
        if 'cs_order' in reader.metainfo:
            xsec.info.order = reader.metainfo["cs_order"]
        else:
            # Assume LO xsecs, if not defined in the reader
            xsec.info.order = 0
        wlabel = str( sqrtS / TeV ) + ' TeV'
        if xsec.info.order == 0:
            wlabel += ' (LO)'
        elif xsec.info.order == 1:
            wlabel += ' (NLO)'
        elif xsec.info.order == 2:
            wlabel += ' (NLL)'
        xsec.info.label = wlabel
        xsec.value = 0. * pb
        xsec.pid = pid
        # If addEvents = False, set cross-section value to event weight
        if not addEvents:
            xsec.value = eventCs
        xSecsInFile.add(xsec)
    # If addEvents = True, sum up event weights with same mothers
    if addEvents:
        for pid in allpids:
            for ixsec, xsec in enumerate(xSecsInFile.xSections):
                if xsec.pid == pid:
                    xSecsInFile.xSections[ixsec].value += eventCs

    return xSecsInFile


def getParticleInfoFrom(lheInput, pidDict):
    """
    Adds mass, width and decay info from the LHE file to the particles
    in pidDict.
    :parameter slhaInput: path to the LHE file or LheReader object
    :parameter pidDict: A dictionary with pid : Particle object
    
    :return: the lheParticle dictionary with added info
    """
    
    if isinstance(lheInput,LheReader):
        reader = lheInput
        reader.reset()
    elif isinstance(lheInput,str):
        reader = LheReader(lheInput)
    else:
        logger.error("Wrong input format")
        raise SModelSError()
    
    for event in reader:
        vertexDict  = {}
        for lheParticle in event.particles:
            if not lheParticle.pdg in pidDict:
                logger.error("Particle PDG %i was not define. Please add it to the lheParticle definitions" %lheParticle.pdg)
                raise SModelSError()
            #Get the lheParticle and add the mass info:
            p = pidDict[lheParticle.pdg]
            p.addProperty('mass',lheParticle.mass*GeV)            
            #Check where the lheParticle comes from:
            if lheParticle.status == -1:  #Skip initial state
                continue
            #Loop through mothers
            for ip in lheParticle.moms:                
                ip -= 1 #Convert position in event to position in list
                if ip < 0: continue #Skip initial state
                if event.particles[ip].status == -1:
                    continue
                #Now add decay info to the corresponding vertex (indexed by the mother position):
                if not ip in vertexDict:
                    momp = pidDict[event.particles[ip].pdg]
                    vertexDict[ip] = {'inParticle' : momp, 'outParticles' : [p]}
                else:
                    vertexDict[ip]['outParticles'].append(p)
        
        #Now add the vertices from the event to the particles dictionary
        #If vertex already exists, simply add the branching ratio
        for vInfo in vertexDict.values():
            mom = vInfo['inParticle']
            if mom.zParity > 0:  #Ignore decays of even particles
                continue
            v = Vertex(inParticle=mom, outParticles=vInfo['outParticles'], br = 1.)
            if not hasattr(mom,'_decayVertices') or not mom._decayVertices:
                mom._decayVertices = [v]
            else:
                index = index_bisect(mom._decayVertices,v)
                if index != len(mom._decayVertices) and mom._decayVertices[index] == v:
                    mom._decayVertices[index].br += v.br
                else:
                    mom._decayVertices.insert(index,v)
    
    #Now renormalize the BRs and add "fake" widths (equal to the number of decaying events in GeV):
    for p in pidDict.values():
        brTotal = 0.
        if not hasattr(p,'_decayVertices'):
            p._decayVertices = []
        for v in p._decayVertices:
            brTotal += v.br
        width = brTotal*GeV
        p.addProperty('_width',width,overwrite=True)
        for v in p._decayVertices:
            v.br = v.br/brTotal

    return pidDict


class LheReader(object):
    """
    An instance of this class represents a reader for LHE files.
    
    """
    def __init__(self, filename, nmax=None):
        """
        Constructor.
        
        :param filename: LHE file name
        :param nmax: When using the iterator, then nmax is the maximum number
        of events to be reader, nmax=None means read till the end of the file.
        If filename is not a string, assume it is already a file object and do
        not open it.        
        """
        self.filename = filename
        self.nmax = nmax
        self.ctr = 0
        if type(filename) == type('str'):
            self.file = open(filename, 'r')
        else: self.file = filename
        self.metainfo = {"nevents" : None, "totalxsec" : None, "sqrts" : None}
        
        
        # Get global information from file (cross-section sqrts, total
        # cross-section, total number of events)
        self.file.seek(0)
        line = self.file.readline()
        nevts = None
        totxsec = None
        sqrts = None
        # Exit if reached end of events or file
        while not "</LesHouchesEvents>" in line and line != "":
            if "<init>" in line:
                line = self.file.readline()
                if line.split()[0] == line.split()[1] == "2212":
                    sqrts = (eval(line.split()[2]) + eval(line.split()[3])) / 1000. * TeV
                    self.metainfo["sqrts"] = sqrts
                else: break
                line = self.file.readline()
                while not "</init>" in line:
                    if totxsec is None: totxsec = 0*pb
                    totxsec += eval(line.split()[0])* pb
                    line = self.file.readline()
                self.metainfo["totalxsec"] = totxsec
            elif "<event>" in line:
                if nevts is None: nevts = 0
                nevts += 1
            line = self.file.readline()
        self.metainfo["nevents"] = nevts
        # Return file to initial reader position
        self.file.seek(0)
                


    def next(self):
        """
        Get next element in iteration.
        
        Needed for the iterator.
        
        """
        if self.nmax != None and self.ctr == self.nmax:
            raise StopIteration
        e = self.event()
        if e == None:
            raise StopIteration
        return e


    def __iter__(self):
        """
        Make class iterable.
        
        Allows iterations like 'for a in lhereader: print a'.
        
        """
        return self


    def event(self):
        """
        Get next event.
        
        :returns: SmsEvent; None if no event is left to be read.
        
        """
        line = " "
        self.ctr += 1
        ret = SmsEvent(self.ctr)
        # Pass metainfo from file to event
        for (key, value) in self.metainfo.items():
            ret.metainfo[key] = value
        # Find next event
        while line.find("<event>") == -1:
            if line == '':
                return None
            line = self.file.readline()
        # Read event info
        line = self.file.readline()

        # Get particles info
        line = self.file.readline()
        while line.find("</event>") == -1:
            if line.find("#") > -1:
                line = line[:line.find('#')]
            if len(line) == 0:
                line = self.file.readline()
                continue
            particle = LHEParticle()
            linep = [float(x) for x in line.split()]
            if len(linep) < 11:
                logger.error("Line >>%s<< in %s cannot be parsed",
                             line, self.filename)
                line = self.file.readline()
                continue
            particle.pdg = int(linep[0])
            particle.status = int(linep[1])
            particle.moms = [int(linep[2]), int(linep[3])]
            particle.px = linep[6]
            particle.py = linep[7]
            particle.pz = linep[8]
            particle.e = linep[9]
            particle.mass = linep[10]

            ret.add(particle)
            line = self.file.readline()
        return ret


    def reset(self):
        """
        Restores the reader to its initial state
        """
        
        self.file.seek(0)
        self.ctr = 0

    def close(self):
        """
        Close the lhe file, if open.
        
        """
        self.file.close()



class SmsEvent(object):
    """
    Event class featuring a list of particles and some convenience functions.
    
    """
    def __init__(self, eventnr=None):
        self.particles = []
        self.eventnr = eventnr
        self.metainfo = {}


    def metaInfo(self, key):
        """
        Return the meta information of 'key', None if info does not exist.
        
        """
        if not key in self.metainfo:
            return None
        return self.metainfo[key]

    def add(self, particle):
        """
        Add particle to the event.
        
        """
        self.particles.append(particle)


    def getMom(self):
        """
        Return the pdgs of the mothers, None if a problem occurs.
        
        """
        momspdg = []
        imom = 0
        for p in self.particles:
            if len(p.moms) > 1 and p.moms[0] == 1 or p.moms[1] == 1:
                momspdg.append(p.pdg)
                imom += 1
        if imom != 2:
            logger.error("Number of mother particles %d != 2", imom)
            raise SModelSError()
        if momspdg[0] > momspdg[1]:
            momspdg[0], momspdg[1] = momspdg[1], momspdg[0]
        return momspdg


    def __str__(self):
        nr = ""
        if self.eventnr != None:
            nr = " " + str(self.eventnr)
        metainfo = ""
        for(key, value) in self.metainfo.items():
            metainfo += " %s:%s" % (key, value)
        ret = "\nEvent%s:%s\n" % (nr, metainfo)
        for p in self.particles:
            ret += p.__str__() + "\n"
        return ret


class LHEParticle(object):
    """
    An instance of this class represents a particle.
    
    """
    def __init__(self):
        self.pdg = 0
        self.status = 0
        # moms is a list of the indices of the mother particles
        self.moms = []
        self.px = 0.
        self.py = 0.
        self.pz = 0.
        self.e = 0.
        self.mass = 0.
        # position in the event list of particles
        self.position = None

    def __str__(self):
        return "particle pdg %d p=(%.1f,%.1f,%.1f,m=%.1f) status %d moms %s" \
                % (self.pdg, self.px, self.py, self.pz, self.mass,
                   self.status, self.moms)
