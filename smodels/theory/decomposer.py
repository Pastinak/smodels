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
from smodels.theory.exceptions import SModelSTheoryError as SModelSError
import logging

logger = logging.getLogger(__name__)

def decompose(xsecsDict,modelParticles, sigcut=.1 * fb, doCompress=False, doInvisible=False,
              minmassgap=-1.*GeV):
    """
    Perform decomposition using the model input (either LHE or SLHA).
    
    :param modelParticles: A list of all model particles. The decays and widths
                      for each particle have been set already.
    :param xsections: A dictionary with the all production cross-sections.
                      The keys must be tuple with the produced particles
                      and the values the respective XSectionList objects                       
    :param sigcut: minimum sigma*BR to be generated, by default sigcut = 0.1 fb
    :param doCompress: turn mass compression on/off
    :param doInvisible: turn invisible compression on/off
    :param minmassgap: maximum value (in GeV) for considering two R-odd particles
                       degenerate (only revelant for doCompress=True )
    :returns: list of topologies (TopologyList object)

    """
    t1 = time.time()

    if doCompress and minmassgap / GeV < 0.:
        logger.error("Asked for compression without specifying minmassgap. Please set minmassgap.")        
        raise SModelSError()

    if type(sigcut) == type(1.):
        sigcut = sigcut * fb
        
    #Generate a dictionary of produced particles and their maximum xsecs:
    producedPartsDict = {}
    for ppair,xsec in xsecsDict.items():
        if xsec.getMaxXsec() < sigcut:
            continue  #Skip cross-sections with too low values
        for p in ppair:
            if not p in producedPartsDict:
                producedPartsDict[p] = xsec.getMaxXsec()
            else:
                producedPartsDict[p] = max(producedPartsDict[p],xsec.getMaxXsec())
    
    #Check if all produced particles have been defined
    for p in producedPartsDict:
        if not p in modelParticles:
            logger.error("Produced particle %s does not appear in modelParticles" %str(p))
            raise SModelSError()
    
        
    # Create 1-particle branches with all primary vertices
    branchDict = {}
    for particle,xsec in producedPartsDict.items():
        #Create branches with production vertices
        v = Vertex(inParticle = None, outParticles=[particle])
        b = Branch(vertices=[v])
        b.maxWeight = xsec
        branchDict[particle] = [b]

    
    # Generate final branches (after all R-odd particles have decayed)
    for particle,b0 in branchDict.items():
        branchDict[particle] = sorted(decayBranches(b0,sigcut), 
                                      key=lambda b: b.maxWeight, reverse=True)
    
    smsTopList = topology.TopologyList()
    # Combine pairs of branches into elements according to production
    # cross-section list
    for ppair,xsec in xsecsDict.items():        
        minBR = (sigcut/xsec.getMaxXsec()).asNumber()
        if minBR > 1.: continue
        for branch1 in branchDict[ppair[0]]:
            BR1 = branch1.maxWeight/producedPartsDict[ppair[0]]  #Branching ratio for first branch            
            if BR1 < minBR: break  #Stop loop if BR1 is already too low            
            for branch2 in branchDict[ppair[1]]:
                BR2 = branch2.maxWeight/producedPartsDict[ppair[1]]  #Branching ratio for second branch
                if BR2 < minBR: break  #Stop loop if BR2 is already too low
                
                finalBR = BR1*BR2                
                if type(finalBR) == type(1.*fb):
                    finalBR = finalBR.asNumber()
                if finalBR < minBR: continue # Skip elements with xsec below sigcut

                newElement = element.Element(branches=[branch1.copy(), branch2.copy()])
                newElement.weight = xsec*finalBR
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