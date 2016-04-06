#!/usr/bin/env python

"""
.. module:: theory.slhaDecomposer
   :synopsis: Decomposition of SLHA events and creation of TopologyLists.

.. moduleauthor:: Andre Lessa <lessa.a.p@gmail.com>
.. moduleauthor:: Wolfgang Waltenberger <wolfgang.waltenberger@gmail.com>

"""

import copy
import time
from smodels.theory import element, topology, crossSection
from smodels.theory.branch import Branch, decayBranches
from smodels.theory.vertex import Vertex, createVertexFromDecay
import pyslha
from smodels.tools.physicsUnits import fb, GeV
from smodels.particleDefinitions import useParticlesPidDict
from smodels.theory.exceptions import SModelSTheoryError as SModelSError
import logging

logger = logging.getLogger(__name__)

def decompose(slhafile, sigcut=.1 * fb, doCompress=False, doInvisible=False,
              minmassgap=-1.*GeV, useXSecs=None):
    """
    Perform SLHA-based decomposition.
    
    :param sigcut: minimum sigma*BR to be generated, by default sigcut = 0.1 fb
    :param doCompress: turn mass compression on/off
    :param doInvisible: turn invisible compression on/off
    :param minmassgap: maximum value (in GeV) for considering two R-odd particles
                       degenerate (only revelant for doCompress=True )
    :param useXSecs: optionally a dictionary with cross-sections for pair
                 production, by default reading the cross sections
                 from the SLHA file.
    :returns: list of topologies (TopologyList object)

    """
    t1 = time.time()

    if doCompress and minmassgap / GeV < 0.:
        logger.error("Asked for compression without specifying minmassgap. Please set minmassgap.")        
        raise SModelSError()

    if type(sigcut) == type(1.):
        sigcut = sigcut * fb

    # Get cross-section from file
    xSectionList = crossSection.getXsecFromSLHAFile(slhafile, useXSecs)
    # Only use the highest order cross-sections for each process
    xSectionList.removeLowerOrder()    
    # Add mass, width and decay information from SLHA file to the defined particles
    particlesDict = _addInfoFrom(slhafile,useParticlesPidDict)
    # Order xsections by PDGs to improve performance
    xSectionList.order()

    # Get maximum cross-sections (weights) for single particles (irrespective
    # of sqrtS)
    maxWeight = {}
    for pid in xSectionList.getPIDs():
        maxWeight[pid] = xSectionList.getXsecsFor(pid).getMaxXsec()    

    # Generate dictionary, where keys are the PIDs and values 
    # are the list of cross-sections for the PID pair (for performance)
    xSectionListDict = {}    
    for pids in xSectionList.getPIDpairs():
        xSectionListDict[pids] = xSectionList.getXsecsFor(pids)

    # Create 1-particle branches with all primary vertices
    branchList = []
    for pid in maxWeight:
        if maxWeight[pid].value < sigcut:  #Skip too low cross-sections
            continue
        if not pid in particlesDict:
            logger.warning( "Particle with PDG = %i was not defined. Cross-section will be ignored" 
                            %pid)
            continue
        #Create branches with production vertices
        v = Vertex(inParticle = None, outParticles=[particlesDict[pid]])
        b = Branch(vertices=[v])
        b.maxWeight = maxWeight[pid]
        branchList.append(b)

    
    # Generate final branches (after all R-odd particles have decayed)    
    finalBranchList = decayBranches(branchList,sigcut)
    # Generate dictionary, where keys are the PIDs and values are 
    #the list of branches for the PID (for performance)
    branchListDict = {}
    for branch in finalBranchList:
        pid = branch.vertices[0].outOdd[0]._pid
        if pid in branchListDict:
            branchListDict[pid].append(branch)
        else:
            branchListDict[pid] = [branch]
    for pid in xSectionList.getPIDs():
        if not pid in branchListDict: branchListDict[pid] = []

    #Sort the branch lists by max weight to improve performance:
    for pid in branchListDict:
        branchListDict[pid] = sorted(branchListDict[pid], 
                                     key=lambda br: br.maxWeight, reverse=True)
    
    smsTopList = topology.TopologyList()
    # Combine pairs of branches into elements according to production
    # cross-section list
    for pids in xSectionList.getPIDpairs():
        weightList = xSectionListDict[pids]
        minBR = (sigcut/weightList.getMaxXsec()).asNumber()
        if minBR > 1.: continue
        for branch1 in branchListDict[pids[0]]:
            BR1 = branch1.maxWeight/maxWeight[pids[0]]  #Branching ratio for first branch            
            if BR1 < minBR: break  #Stop loop if BR1 is already too low            
            for branch2 in branchListDict[pids[1]]:
                BR2 = branch2.maxWeight/maxWeight[pids[1]]  #Branching ratio for second branch
                if BR2 < minBR: break  #Stop loop if BR2 is already too low
                
                finalBR = BR1*BR2                
                if type(finalBR) == type(1.*fb):
                    finalBR = finalBR.asNumber()
                if finalBR < minBR: continue # Skip elements with xsec below sigcut

                if len(branch1.PIDs) != 1 or len(branch2.PIDs) != 1:
                    logger.error("During decomposition the branches should \
                            not have multiple PID lists!")
                    return False    

                newElement = element.Element(branches=[branch1.copy(), branch2.copy()])
                newElement.weight = weightList*finalBR
                allElements = [newElement]
                # Perform compression
                if doCompress or doInvisible:
                    allElements += newElement.compressElement(doCompress,
                                                                  doInvisible,
                                                                  minmassgap)

                for el in allElements:
                    el.sortBranches()  #Make sure elements are sorted BEFORE adding them                    
                    smsTopList.addElement(el)                    
    smsTopList._setElementIds()

    logger.debug("slhaDecomposer done in " + str(time.time() - t1) + " s.")
    return smsTopList


def _addInfoFrom(slhafile, pidDict):
    """
    Adds mass, width and decay info from the SLHA file to the particles
    in pidDict.
    :parameter slhafile: path to the SLHA file
    :parameter pidDict: A dictionary with pid : Particle object
    """
    
    try:
        f=pyslha.read(slhafile)
    except pyslha.ParseError,e:
        logger.error ( "The file %s cannot be parsed as an SLHA file: %s" % (slhafile, e) )
        raise SModelSError()

    # Assign masses and BRs to particles in useParticles
    for pid in f.blocks["MASS"].keys():
        if not pid in pidDict:
            logger.warning("Particle with PDG %i was not defined and will be ignored." %pid)
            continue
        p = pidDict[pid]
        p.addProperty('mass',f.blocks["MASS"][pid]*GeV,overwrite=False)
        p._width = None
        p._decayVertices = None
        if p.zParity > 0:            
            logger.info("Ignoring decays of even particle %s" %p._name)
            continue
        if pid in f.decays:
            p.addProperty('_width',f.decays[pid].totalwidth*GeV)            
            if f.decays[pid].totalwidth:
                p._decayVertices = []
                for decay in f.decays[pid].decays:
                    p._decayVertices.append(createVertexFromDecay(decay,inPDG = p._pid))
    return pidDict