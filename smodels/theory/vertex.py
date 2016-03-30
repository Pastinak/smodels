#!/usr/bin/env python

"""
.. module:: theory.vertex
   :synopsis: Defines the vertex class and its methods

.. moduleauthor:: Andre Lessa <lessa.a.p@gmail.com>

"""

import logging
from smodels.theory.particle import Particle
from smodels.theory.exceptions import SModelSTheoryError as SModelSError
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
        self.sortParticles()

        #Split outgoing particles into even and odd
        self.outEven = []
        self.outOdd = []
        for p in self.outParticles:
            if p.zParity == +1:
                self.outEven.append(p)
            elif p.zParity == -1:
                self.outOdd.append(p)
                
        if not self.sanityCheck():
            logger.error("Wrong vertex structure.")
            raise SModelSError
        
    def __str__(self):
        """
        Default string representation (particle names for the outgoing even particles)
        :return: list of outgoing even particle names
        """
        
        return str([str(p) for p in self.outEven])
    
    def stringRep(self):
        """
        Extended string representation.
        :return: string represantion in the format inParticle --> oddParticle + [evenParticles]
        """
        
        strR = self.inParticle.name + ' --> ' + self.outOdd[0].name 
        strR += ' + ' + str(self)
        
        return strR
    
    def sortParticles(self):
        """
        Sorts the vertex particles according to their names
        """
        
        self.outParticles = sorted(self.outParticles, key=lambda p: p.name)
        
    def sanityCheck(self):
        """
        Makes sure the vertex has the correct structure: 1 incoming Z2-odd particle,
        1 outgoing Z2-odd particle and N-2 Z2-even outgoing particles
        
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
