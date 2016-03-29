#!/usr/bin/env python

"""
.. module:: theory.vertex
   :synopsis: Defines the vertex class and its methods

.. moduleauthor:: Andre Lessa <lessa.a.p@gmail.com>

"""

import unum
import logging
from smodels.theory.particle import Particle
from smodels.theory.exceptions import SModelSTheoryError as SModelSError
logger = logging.getLogger(__name__)


class Vertex(object):
    """
    An instance of this class represents a vertex (belonging to a branch/element).    

    """
    def __init__(self, particles=[]):
        """
        Initializes the vertex.
        
        :parameter particles: List of particles (Particle objects)
        """
                
        if not isinstance(particles,list):
            logger.error("Particles must be a list and not %s" %str(type(particles)))
            raise SModelSError
        else:
            for p in particles:
                if not isinstance(p,Particle):
                    logger.error("Particle must be a Particle object and not %s" %str(type(p)))
                    raise SModelSError
        self.particles = particles
        
    def __eq__(self,other):
        """
        Checks if the vertices are equal. Compares the particles in each vertex
        """
        
        return self.particles == other.particles         
        
    def __str__(self):
        """
        String represantion (particle name)
        """
        
        return [str(p) for p in self.particles]
    
    def copy(self):
        """
        Generates a copy of the particle  
        """
        
        newP = Particle()
        newP.name = self.name
        newP.mass = self.mass
        newP.pid = self.pid
        newP.spin = self.spin
        newP.eCharge = self.eCharge
        newP.qColor = self.qColor
        newP.zParity = self.zParity
        
        return newP
