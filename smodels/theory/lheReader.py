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
from smodels.theory.particle import ParticleList
from smodels.theory.vertex import Vertex
from smodels.tools.physicsUnits import TeV, pb, GeV
from smodels.theory.exceptions import SModelSTheoryError as SModelSError

logger = logging.getLogger(__name__)

def getInputData(lhefile, modelParticles):
    """
    Get model information from LHE file.
    :param lhefile: path to the LHE file 
    :param modelParticles: a list with all the model particles. Each
                           particle must contain a _pid property.
    
    :returns: XSection dictionary and particles list
    """
    
    try:
        reader = LheReader(lhefile)
    except:
        logger.info("The file %s cannot be parsed as a LHE file: %s" % (lhefile) )
        raise SModelSError()
    
    #Create a PID dictionary of single particles
    pidDict = {}
    for p in modelParticles:
        if isinstance(p,ParticleList): continue
        if not hasattr(p,'_pid'):
            logger.error("Particle %s does not have a _pid" %str(p))
            raise SModelSError()
        if p._pid in pidDict:
            logger.error("Multiple definitions of particle PID %i" %p._pid)
            raise SModelSError()
        pidDict[p._pid] = p    

    # Get cross-section from LHE file
    xSectionList = getXsecsFrom(reader)
    # Only use the highest order cross-sections for each process
    xSectionList.removeLowerOrder()
    # Order xsections by PDGs to improve performance
    xSectionList.order()    
    # Add mass, width and decay information from SLHA file to the defined particles
    particlesDict = getParticleInfoFrom(reader,pidDict)
    reader.close()
    
    #Generate cross-section dictionary
    xSectionDict = {}
    for xsec in xSectionList:
        pids = sorted(xsec.pid)
        ppair = (particlesDict[pids[0]],particlesDict[pids[1]])
        if not ppair in xSectionDict:
            xSectionDict[ppair] = XSectionList()
        xSectionDict[ppair].add(xsec)
    
    particleList = particlesDict.values()
    
    return xSectionDict,particleList

def getXsecsFrom(lheInput):
    """
    Obtain cross-sections from input LHE file.
    
    :parameter lheInput: LHE input file with unweighted MC events or a LheReader object
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
        logger.info("Cross-section information not found in LHE file.")        
        raise SModelSError()
    elif not reader.metainfo["nevents"]:
        logger.info("Total number of events information not found in LHE " +
                     "file.")
        raise SModelSError()
    elif not type ( reader.metainfo["sqrts"] ) == type ( TeV ):
        logger.info("Center-of-mass energy information not found in LHE " +
                     "file.")
        raise SModelSError()

    # Common cross-section info
    totxsec = reader.metainfo["totalxsec"]
    nevts = reader.metainfo["nevents"]
    sqrtS = reader.metainfo["sqrts"]
    eventCs = totxsec / float(nevts)


    # Loop over events, create a XSection for each event corresponding
    #to its weight and add it to the list (if the xsec already is in the list its weight
    #will be combined)
    for event in reader:
        pids = tuple(sorted(event.getMom()))
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
        xsec.value = eventCs
        xsec.pid = pids
        xSecsInFile._addValue(xsec)

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
    
    vertexPidDict = {}
    for event in reader:
        vertexInfo  = {}
        for lheParticle in event.particles:
            if not lheParticle.pdg in pidDict:
                logger.error("Particle PDG %i was not define. Please add it to the lheParticle definitions" %lheParticle.pdg)
                raise SModelSError()
            #Get the lheParticle and add the mass info:
            p = pidDict[lheParticle.pdg]
            p.addProperty('mass',lheParticle.mass*GeV,overwrite=True)
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
                if not ip in vertexInfo:
                    momp = pidDict[event.particles[ip].pdg]
                    vertexInfo[ip] = {'inParticle' : momp, 'outParticles' : [p]}
                else:
                    vertexInfo[ip]['outParticles'].append(p)
        
        #Now add the vertices from the event to the vertex dictionary
        #If vertex already exists, simply add the branching ratio
        for vInfo in vertexInfo.values():
            mom = vInfo['inParticle']
            if mom.zParity > 0:  #Ignore decays of even particles
                continue
            v = Vertex(inParticle=mom, outParticles=vInfo['outParticles'], br = 1.)
            if not mom._pid in vertexPidDict:
                vertexPidDict[mom._pid] = [v]
            else:
                index = index_bisect(vertexPidDict[mom._pid],v)
                if index != len(vertexPidDict[mom._pid]) and vertexPidDict[mom._pid][index] == v:
                    vertexPidDict[mom._pid][index].br += v.br
                else:
                    vertexPidDict[mom._pid].insert(index,v)


    #First clear previously defined decays
    for pid,p in pidDict.items():
        if p.zParity > 0:  #Does not modify decays of even particles
            continue
        p._decayVertices = []
        p._witdh = None        
   
    #Now renormalize the BRs, compute "fake" widths (equal to the number of decaying events in GeV)
    #and add the vertices to the respective pre-defined particles            
    for pid,vertices in vertexPidDict.items():        
        brTotal = 0.
        p = pidDict[pid]
        for v in vertices:
            brTotal += v.br
        width = brTotal*GeV
        p.addProperty('_width',width,overwrite=True)
        for v in vertices:
            v.br = v.br/brTotal
        p._decayVertices = vertices
        

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
