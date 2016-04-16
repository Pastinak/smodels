#!/usr/bin/env python

"""
.. module:: theory.decomposer
   :synopsis: Decompose a model: build elements from model input and add them to a TopolofyList.
              Uses lheReader for a LHE input file or slhaReader for a SLHA input file.
.. moduleauthor:: Andre Lessa <lessa.a.p@gmail.com>
.. moduleauthor:: Wolfgang Waltenberger <wolfgang.waltenberger@gmail.com>

"""

import time
from smodels.theory import element, topology
from smodels.theory.branch import Branch, decayBranches
from smodels.theory.vertex import Vertex
from smodels.tools.physicsUnits import fb, GeV
from smodels.particleDefinitions import useParticlesPidDict
from smodels.theory.exceptions import SModelSTheoryError as SModelSError
from smodels.theory import lheReader, slhaReader
import logging

logger = logging.getLogger(__name__)

def decompose(inputfile, sigcut=.1 * fb, doCompress=False, doInvisible=False,
              minmassgap=-1.*GeV, useXSecs=None):
    """
    Perform decomposition using the model input (either LHE or SLHA).
    
    :param inputfile: A SLHA or LHE input file.
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
        
    #Get cross-sections and particle information from input file:
    try:
        inputData = lheReader.getInputData(inputfile)
    except:    
        try:
            inputData = slhaReader.getInputData(inputfile)
        except:
                logger.error("Could not read input as SLHA  or LHE file.")
                raise SModelSError()

    xSectionList, particlesDict = inputData

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
        if maxWeight[pid] < sigcut:  #Skip too low cross-sections
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