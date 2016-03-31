#!/usr/bin/env python

"""
.. module:: theory.vertex
   :synopsis: Defines the vertex class and its methods

.. moduleauthor:: Andre Lessa <lessa.a.p@gmail.com>

"""

import logging
from smodels.theory.particle import Particle
from smodels.theory.exceptions import SModelSTheoryError as SModelSError
from smodels.theory.auxiliaryFunctions import stringToList
logger = logging.getLogger(__name__)


class Vertex(object):
    """
    An instance of this class represents a vertex (belonging to a branch/element).    

    """
    def __init__(self, inParticle=None, outParticles=[]):
        """
        Initializes the vertex.
        
        :parameter inParticle: incoming particle (Particle object)
        :parameter outParticles: List of outgoing particles (Particle objects)
        """
          
        if (not inParticle is None) and (not isinstance(inParticle, Particle)):
            logger.error("inParticle must be a Particle object and not %s" %str(type(inParticle)))
            raise SModelSError
        self.inParticle = inParticle
        
        if not isinstance(outParticles,list):
            logger.error("outParticles must be a list and not %s" %str(type(outParticles)))
            raise SModelSError
        else:
            for p in outParticles:
                if not isinstance(p,Particle):
                    logger.error("Particle must be a Particle object and not %s" %str(type(p)))
                    raise SModelSError
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
            raise SModelSError
        
    def __str__(self):
        """
        Default string representation (particle names for the outgoing even particles)
        :return: list of outgoing even particle names
        """
        
        return str(self.getEvenNameList()).replace("'","").replace(" ","")
    
    def getEvenNameList(self):
        """
        Returns a sorted list with the names of outgoing even particles  
        """
        
        return sorted([str(p) for p in self.outEven])
    
    def getOddMassList(self):
        """
        Returns a list with the masses of outgoing odd particles  
        """
        
        return [p.mass for p in self.outOdd]
        
    
    def __cmp__(self,other):
        """
        Compares the vertex with other.        
        The comparison is made based on the number of particles in the vertex, 
        then on the size of the outgoing even particles, then the odd particles 
        and finally the incoming particle (see particle.__cmp__).
        OBS: The particles inside each vertex MUST BE sorted (see vertex.sortParticles())         
        :param other:  vertex to be compared (Vertex object)
        :return: -1 if self < other, 0 if self == other, +1, if self > other.
        """
        
        if len(self.outParticles) != len(other.outParticles):
            comp = len(self.outParticles) > len(other.outParticles)
            if comp: return 1
            else: return -1
        elif self.outEven != other.outEven:
            comp = self.outEven > other.outEven
            if comp: return 1
            else: return -1
        elif self.outOdd != other.outOdd:  
            comp = self.outOdd > other.outOdd
            if comp: return 1
            else: return -1
        elif self.inParticle != other.inParticle:
            comp = self.inParticle > other.inParticle
            if comp: return 1
            else: return -1
       
        else:
            return 0    #Vertices are equal   
    
    
    def stringRep(self):
        """
        Extended string representation.
        :return: string represantion in the format inParticle --> oddParticle + [evenParticles]
        """
        
        strR = str(self.inParticle) + ' --> ' + str(self.outOdd[0]) 
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
        Makes sure the vertex has the correct structure: 1 incoming Z2-odd particle,
        1 outgoing Z2-odd particle and n-2 Z2-even outgoing particles
        
        :return: True if the structure is correct, False otherwise
        """
        
        if not self.inParticle.zParity == -1:
            logger.error("Vertex does not have one incoming Z2-odd particle")
            return False
        
        if len(self.outOdd) != 1:
            logger.error("Vertex does not have one outgoing Z2-odd particle")
            return False
        
        if len(self.outEven) + len(self.outOdd) != len(self.outParticles):
            logger.error("Number of odd and even parities is not equal to the total number of particles")
            return False         
        
        return True
    
    def copy(self):
        """
        Generates a copy of the particle  
        :return: copy of itself (Vertex object)
        """
        
        newV = Vertex(inParticle=self.inParticle.copy(), 
                      outParticles=[p.copy() for p in self.outParticles])
        if hasattr(self, 'br'): newV.br = self.br
        
        return newV    

def createVertexFromStr(vertexStr):
    """
    Creates a vertex from a string in bracket notation (e.g. [e+,jet])
    Odd-particles are created as empty Particle objects and Even-particles only have 
    the corresponding name.
    :branchStr: vertexStr (e.g. [e+,jet])
    :return: Branch object
    """
    
    #Define empty incoming and outgoing odd particles
    inParticle = Particle(zParity = -1)
    outParticles = [Particle(zParity = -1)]
    for pname in stringToList(vertexStr):
        if not isinstance(pname,str):
            logger.error("Error converting vertex string %s" %vertexStr)
            raise SModelSError
        outParticles.append(Particle(zParity = +1, name = pname))
    
    return Vertex(inParticle=inParticle, outParticles=outParticles)