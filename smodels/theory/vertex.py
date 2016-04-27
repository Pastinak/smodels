#!/usr/bin/env python

"""
.. module:: theory.vertex
   :synopsis: Defines the vertex class and its methods

.. moduleauthor:: Andre Lessa <lessa.a.p@gmail.com>

"""

import logging
from smodels.theory.particle import Particle, ParticleList
from smodels.theory.exceptions import SModelSTheoryError as SModelSError
from smodels.theory.auxiliaryFunctions import stringToList
import itertools
import copy

logger = logging.getLogger(__name__)


class Vertex(object):
    """
    An instance of this class represents a vertex (belonging to a branch/element).    

    """
    def __init__(self, inParticle=None, outParticles=[], br = None):
        """
        Initializes the vertex.
        
        :parameter inParticle: incoming particle (Particle object)
        :parameter outParticles: List of outgoing particles (Particle objects)
        :parameter br: Corresponding branching ratio for the vertex (optional)
        """
        
        self.br = br
          
        if (not inParticle is None) and (not isinstance(inParticle, Particle)):
            logger.error("inParticle must be a Particle object and not %s" %str(type(inParticle)))
            raise SModelSError()
        self.inParticle = inParticle
        
        if not isinstance(outParticles,list):
            logger.error("outParticles must be a list and not %s" %str(type(outParticles)))
            raise SModelSError()
        else:
            for p in outParticles:
                if not isinstance(p,Particle) and not isinstance(p,ParticleList):
                    logger.error("Particle must be a Particle or ParticleList object and not %s" %str(type(p)))
                    raise SModelSError()
        self.outParticles = outParticles

        #Split outgoing particles into even and odd
        self.outEven = []
        self.outOdd = []
        for p in self.outParticles:
            if p.zParity == +1:
                self.outEven.append(p)
            elif p.zParity == -1:
                self.outOdd.append(p)
        
        self.sortParticles()
        if not self.sanityCheck():
            logger.error("Wrong vertex structure.")
            raise SModelSError()
        
    def __str__(self):
        """
        Default string representation (particle names for the outgoing even particles)
        :return: list of outgoing even particle names
        """
        
        st = str([str(p) for p in self.outEven]).replace("'","").replace(" ","")
        
        return st


    def __cmp__(self,other):
        """
        Compares the vertex with other.        
        The comparison is made based on the number of particles in the vertex, 
        then on the size of the outgoing even particles, then the odd particles 
        and finally the incoming particle (see particle.__cmp__).
        The particle ordering inside each vertex is not taken into account.
        OBS: The vertices should be sorted (see vertex.sortParticles()) in
        order for the > (<) comparison to make sense.                
        :param other:  vertex to be compared (Vertex object)
        :return: -1 if self < other, 0 if self == other, +1, if self > other.
        """
        
        if not isinstance(other,Vertex):
            return +1
        
        #First check overall number of total, even and odd outgoing particles
        cmpOut = cmp(len(self.outParticles),len(other.outParticles))
        if cmpOut:
            return cmpOut #Number of total particles do not match
        cmpEven = cmp(len(self.outEven),len(other.outEven))
        if cmpEven:
            return cmpEven #Number of even particles do not match
        cmpOdd = cmp(len(self.outOdd),len(other.outOdd))
        if cmpOdd:
            return cmpOdd #Number of odd particles do not match

        #Compare outgoing even particles (irrespective of order)
        evenList = [list(v) for v in itertools.permutations(self.outEven)]
        match = False
        for v in evenList:
            if v == other.outEven:
                match = True
                break
        if not match:
            return cmp(self.outEven,other.outEven)
        
        #Compare outgoing odd particles (irrespective of order)
        oddList = [list(v) for v in itertools.permutations(self.outOdd)]
        match = False
        for v in oddList:
            if v == other.outOdd:
                match = True
                break
        if not match:
            return cmp(self.outOdd,other.outOdd)
        
        #Compare incoming particle   
        if self.inParticle != other.inParticle:   
            return cmp(self.inParticle,other.inParticle)
                 
        return 0   #Vertices are equal   
    
    
    def describe(self):
        """
        Extended string representation.
        :return: string represantion in the format inParticle --> oddParticle + [evenParticles]
        """
        
        strR = str(self.inParticle) + ' --> ' + str(self.outOdd[0])
        if  self.outEven:
            strR += ' + ' + str(self)
        
        return strR
    
    def sortParticles(self):
        """
        Sorts the vertex particles (see particle.__cmp__ for the Particle comparison)
        """
        
        self.outParticles = sorted(self.outParticles)
        self.outEven = sorted(self.outEven)
        self.outOdd = sorted(self.outOdd)
        
    def sanityCheck(self):
        """
        Makes sure the vertex has the correct structure: 1 (or 0) incoming Z2-odd particle,
        1 outgoing Z2-odd particle and n-2 Z2-even outgoing particles
        
        :return: True if the structure is correct, False otherwise
        """
        
        if self.inParticle and not self.inParticle.zParity == -1:
            logger.error("Vertex does not have one incoming Z2-odd particle:\n %s" %self.describe())
            return False
        
        if len(self.outOdd) != 1:
            logger.error("Vertex does not have one outgoing Z2-odd particle:\n %s" %self.describe())
            return False
        
        if len(self.outEven) + len(self.outOdd) != len(self.outParticles):
            logger.error("Number of odd and even parities is not equal to the total number of particles")
            return False         
        
        return True
    
    def copy(self):
        """
        Generates a new Vertex objected with the same particles 
        (the particle objects are not copied);
        :return: copy of itself (Vertex object)
        """
        
        
        newV = Vertex(inParticle=self.inParticle, outParticles=self.outParticles[:])
        if not self.br is None:
            newV.br = copy.deepcopy(self.br)
                    
        return newV
    
    def combineParticles(self,other):
        """
        Combine the particles of both vertices 
        (replaces the particle by a particle list containing its particles 
        and the particles of other).
        If the new particles already appear in self,  do not add them to the list.
        
        :parameter other: vertex (Vertex Object) 
        """
        
        if len(self.outParticles) != len(other.outParticles):
            logger.error("Error combining elements: number of outParticles differ")
            raise SModelSError()
        
        #Make sure vertices are sorted
        self.sortParticles()
        other.sortParticles()

        #Combine particles (generate a ParticleList if particles are not the same):
        for ip,p in enumerate(self.outParticles):
            self.outParticles[ip] = p.combineWith(other.outParticles[ip])
        
        if self.inParticle and other.inParticle:
            self.inParticle = self.inParticle.combineWith(other.inParticle)
        elif self.inParticle != other.inParticle:
            logger.error("Both incoming particles should be None.")
            raise SModelSError()

        #Split outgoing particles into even and odd
        self.outEven = []
        self.outOdd = []
        for p in self.outParticles:
            if p.zParity == +1:
                self.outEven.append(p)
            elif p.zParity == -1:
                self.outOdd.append(p)
        
        self.sortParticles()
                
    def getOddPIDs(self):
        """
        Return the of PID for the outgoing odd particle.
        If the vertex combines distinct PIDs, returns a list of PIDs.
        :return: PID or list of PIDs 
                (e.g. pidA for a simple vertex)
                (e.g. [pidA1,pidA2,..] for a combined vertex) 
        """
        
        if isinstance(self.outOdd[0],Particle):            
            if hasattr(self.outOdd[0], '_pid'):
                return self.outOdd[0]._pid
            else:
                return None
        elif isinstance(self.outOdd[0],ParticleList): #Combined vertex
            pids = [p._pid for p in self.outOdd[0].particles if hasattr(p,'_pid')]
            pids = list(set(pids))
            if len(pids) == 1:
                return pids[0]
            else:
                return pids 
            

def createVertexFromStr(vertexStr,particleNameDict):
    """
    Creates a vertex from a string in bracket notation (e.g. [e+,jet])
    Odd-particles are created as empty Particle objects and Even-particles
    are created using the particles defined in particleNameDict (by the user) which match the corresponding
    particle label/name.
    :parameter branchStr: vertexStr (e.g. [e+,jet])
    :parameter particleNameDict: Dictionary containing as keys the particle names/labels
                                and as labels the corresponding Particle objects
                                (e.g. {'e-' : Particle(..), 'e+': Particle(..), ...})
    :return: Vertex object
    """
    
    #Define empty incoming and outgoing odd particles
    inParticle = Particle(zParity = -1, _name = "incomingOdd")
    outParticles = [Particle(zParity = -1, _name = "outgoingOdd")]
    for pname in stringToList(vertexStr):
        if not isinstance(pname,str):
            logger.error("Error converting vertex string %s" %vertexStr)
            raise SModelSError()
        if not pname in particleNameDict:
            logger.error("Particle %s has not been defined (see particleDefinitions.py)" %pname)
            raise SModelSError()
        outParticles.append(particleNameDict[pname])
    
    return Vertex(inParticle=inParticle, outParticles=outParticles)
