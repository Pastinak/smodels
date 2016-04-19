#!/usr/bin/env python

"""
.. module:: theory.slhaDecomposer
   :synopsis: Decomposition of SLHA events and creation of TopologyLists.

.. moduleauthor:: Andre Lessa <lessa.a.p@gmail.com>
.. moduleauthor:: Wolfgang Waltenberger <wolfgang.waltenberger@gmail.com>

"""

from smodels.theory.crossSection import XSectionList, XSection
from smodels.theory.vertex import Vertex
from smodels.theory.particle import ParticleList
import pyslha
from smodels.tools.physicsUnits import GeV, pb, TeV
from smodels.theory.exceptions import SModelSTheoryError as SModelSError
import logging

logger = logging.getLogger(__name__)



def getInputData(slhafile, modelParticles):
    """
    Get model information from slhafile.
    
    :param slhafile: path to the SLHA file
    :param modelParticles: a list with all the model particles. Each
                           particle must contain a _pid property.
                 
    :returns: XSection dictionary and particles list

    """
    try:
        pydata = pyslha.read(slhafile)
    except pyslha.ParseError,e:
        logger.info( "The file %s cannot be parsed as an SLHA file: %s" % (slhafile, e) )
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
    # Get cross-section from file
    xSectionList = getXsecsFrom(pydata)
    # Only use the highest order cross-sections for each process
    xSectionList.removeLowerOrder()
    # Order xsections by PDGs to improve performance
    xSectionList.order()        
    # Add mass, width and decay information from SLHA file to the defined particles
    particlesDict = getParticleInfoFrom(pydata,pidDict)
    
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

def getXsecsFrom(slhaInput, useXSecs=None, xsecUnit = pb):
    """
    Obtain cross-sections for pair production of R-odd particles from input SLHA file.
    The default unit for cross-section is pb.
    
    :parameter slhaInput: SLHA input file with cross-sections or pyslha.Doc object
    :parameter useXSecs: if defined enables the user to select cross-sections to
                     use. Must be a XSecInfoList object
    :parameter xsecUnit: cross-section unit in the input file (must be a Unum unit)
    :returns: a XSectionList object    
     
    """
    if isinstance(slhaInput,pyslha.Doc):
        f = slhaInput
    elif isinstance(slhaInput,str):
        f = pyslha.read(slhaInput)
    else:
        logger.error("Wrong input format")
        raise SModelSError()
    
    # Store information about all cross-sections in the SLHA file
    xSecsInFile = XSectionList()
    for production in f.xsections:
        useXSecs = False
        process = f.xsections.get ( production )
        for pxsec in process.xsecs:
            csOrder = pxsec.qcd_order
            wlabel = str( int ( pxsec.sqrts / 1000) ) + ' TeV'
            if csOrder == 0:
                wlabel += ' (LO)'
            elif csOrder == 1:
                wlabel += ' (NLO)'
            elif csOrder == 2:
                wlabel += ' (NLL)'
            else:
                logger.error ( "Unknown QCD order %d" % csOrder )
                raise SModelSError()
            xsec = XSection()
            xsec.info.sqrts = pxsec.sqrts/1000. * TeV
            xsec.info.order = csOrder
            xsec.info.label = wlabel
            xsec.value = pxsec.value * pb
            xsec.pid = production[2:]
            # Do not add xsecs which do not match the user required ones:
            if (useXSecs and not xsec.info in useXSecs):
                continue
            else: xSecsInFile.add(xsec)
            
    return xSecsInFile


def getParticleInfoFrom(slhaInput, pidDict):
    """
    Adds mass, width and decay info from the SLHA file to the particles
    in pidDict.
    :parameter slhaInput: path to the SLHA file or pyslha.Doc object
    :parameter pidDict: A dictionary with pid : Particle object
    
    :return: the particle dictionary with added info
    """
    if isinstance(slhaInput,pyslha.Doc):
        f = slhaInput
    elif isinstance(slhaInput,str):
        f = pyslha.read(slhaInput)
    else:
        logger.error("Wrong input format")
        raise SModelSError()

    
    #First assign masses and widths to particles in useParticles
    for pid in f.blocks["MASS"].keys():
        if not pid in pidDict:
            logger.warning("Particle with PDG %i was not defined and will be ignored." %pid)
            continue
        mass = abs(f.blocks["MASS"][pid])*GeV
        p = pidDict[pid]
        p.addProperty('mass',mass,overwrite=True)
        p.addProperty('_width',f.decays[pid].totalwidth*GeV,overwrite=True)            
        #Add charge conjugate info:
        if -pid in pidDict:
            pidDict[-pid].mass = p.mass
            pidDict[-pid]._width = p._width             
            
    #Now assign the decay vertices:
    for pid in f.decays:    
        if not pid in pidDict:
            logger.warning("Particle with PDG %i was not defined and will be ignored." %pid)
            continue
        p = pidDict[pid]
        if p.zParity > 0:
            continue  #Ignore decays of even particles           
        p._decayVertices = []
        if -pid in pidDict:
            pidDict[-pid]._decayVertices = []
        if f.decays[pid].totalwidth:
            for decay in f.decays[pid].decays:
                decay.parentid = p._pid
                p._decayVertices.append(createVertexFromDecay(decay,pidDict))
            #Add charge conjugate info:
            if not -pid in pidDict: continue            
            for decay in f.decays[pid].decays:
                cdecay = pyslha.Decay(br=decay.br,ids= [- i for i in decay.ids],nda=decay.nda)
                cdecay.parentid = -decay.parentid                
                pidDict[-pid]._decayVertices.append(createVertexFromDecay(cdecay,pidDict))
                
    return pidDict



def createVertexFromDecay(pyslhaDecay,pidDict):
    """
    Creates a vertex from a pyslha Decay obj.
    :parameter pyslhaDecay: pyslha Decay obj
    :parameter inPDG: PDG of the vertex incoming particle
    :parameter pidDict: A dictionary with pid : Particle object    
    :return: Vertex object
    """
    
    if not isinstance(pyslhaDecay,pyslha.Decay):
        logger.error("Input is not a pyslha Decay object!")
        raise SModelSError()
    
    if not pyslhaDecay.parentid:
        inParticle = None
    else:
        if not pyslhaDecay.parentid in pidDict:
            logger.error("Particle PDG %i was not defined" %pyslhaDecay.parentid)
            raise SModelSError()
        inParticle = pidDict[pyslhaDecay.parentid]
    
    outParticles = []
    for pid in pyslhaDecay.ids:
        if not pid in pidDict:
            logger.error("Particle PDG %i was not defined" %pyslhaDecay.parentid)
            raise SModelSError()
        outParticles.append(pidDict[pid])
    v = Vertex(inParticle=inParticle, outParticles=outParticles, br = pyslhaDecay.br)
    
    return v