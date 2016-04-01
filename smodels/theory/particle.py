#!/usr/bin/env python

"""
.. module:: theory.particle
   :synopsis: Defines the particle class, its methods and related functions

.. moduleauthor:: Andre Lessa <lessa.a.p@gmail.com>

"""

import logging
from smodels.theory.exceptions import SModelSTheoryError as SModelSError
import itertools
logger = logging.getLogger(__name__)


class Particle(object):
    """
    An instance of this class represents a single particle.    
    The particle properties are flexible. The only required property is its
    parity.
    """
    def __init__(self, **kwargs):
        """
        Initializes the particle. Allows for flexible particle properties.
        However, the particle Z2-Parity (zParity) MUST always
        be defined.
        
        :parameter zParity: Z2-Parity. -1 for odd particles (neutralino, gluino,...)
                                        and +1 for even particles (quarks, Higgs,...)
        """
        if kwargs is None or not 'zParity' in kwargs:
            logger.error("The Z2-Parity (zParity) of a particle must always be defined")
            raise SModelSError

        for key,value in kwargs.items():
            setattr(self,key,value)

    
    def __cmp__(self,other):
        """
        Compares the particle with other.
        First compare parities, then names (if it exists), then masses (if it exists) then other properties.
        Protected properties of the type '_property' are not used for comparison.
        If other is a ParticleList, uses the ParticleList comparison method.
        :param other:  particle to be compared (Particle object)
        :return: -1 if self < other, 0 if self == other, +1, if self > other.        
        """
        
        if isinstance(other,ParticleList):
            return other.__cmp__(self)
        
        if self.zParity != other.zParity:
            comp = self.zParity > other.zParity
            if comp: return 1
            else: return -1            
        
        if hasattr(self,'name') and hasattr(other,'name'):            
            if self.name != other.name:        
                comp = self.name > other.name
                if comp: return 1
                else: return -1
        if hasattr(self,'mass') and hasattr(other,'mass'):
            if self.mass != other.mass:
                comp = self.mass > other.mass
                if comp: return 1
                else: return -1
        for key in self.__dict__:
            if self.__dict__[key] is None: continue
            if not key in other.__dict__: continue
            if other.__dict__[key] is None: continue
            if key[0] == '_': continue
            if other.__dict__[key] != self.__dict__[key]:
                comp = self.__dict__[key] > other.__dict__[key]
                if comp: return 1
                else: return -1                    
        
        return 0 #Particles are equal
        
        
    def __str__(self):
        """
        String represantion (particle name, if defined)
        :return: Particle name, if defined. Otherwise empty string.
        """
        if hasattr(self, 'name'):
            return self.name
        else:
            return ''
    
    def copy(self):
        """
        Generates a copy of the particle  
        :return: copy of itself (Particle object)
        """
        
        newP = Particle(zParity = self.zParity)
        for key,val in self.__dict__.items():
            setattr(newP,key,val)
        
        return newP
    
    def chargeConjugate(self):
        """
        Returns the charge conjugate particle (flips the sign of eCharge).
        If it has a _pid property also flips its sign.
        The charge conjugate name is defined as the original name plus "*" or
        if the original name ends in "+" ("-"), it is replaced by "-" ("+")
        
        :return: the charge conjugate particle (Particle object)
        """
        
        pConjugate = self.copy()
        if hasattr(pConjugate, 'eCharge'):
            pConjugate.eCharge *= -1
        if hasattr(pConjugate, '_pid'):
            pConjugate._pid *= -1
        if hasattr(pConjugate, 'name'):
            if pConjugate.name[-1] == "+":
                pConjugate.name = pConjugate.name[:-1] + "-"
            elif pConjugate.name[-1] == "-":
                pConjugate.name = pConjugate.name[:-1] + "+"
            else:
                pConjugate.name += "*"
                
        return pConjugate
    
class ParticleList(object):
    """
    An instance of this class represents a list of particles.
    It can be used to group particles (e.g. L+ = [e+,mu+,ta+]).
    """

    def __init__(self, particles=[], label=None):
        """
        Initializes the particle list. Particles can be a list of Particle objects
        and/or ParticleList objects. For the later all the particles in the ParticleList
        are included.
        All the common (shared) properties for all particles in the list are automatically
        attributed to the ParticleList. Properties which are not shared by all the particles
        are set to None.
        The ParticleList name is set to label.
        :param particles: list of single particles or ParticleLists
        :param label: name of the list
        """
                
        self.particles = []
        for p in particles:
            if isinstance(p,Particle):
                self.particles.append(p)
            elif isinstance(p,ParticleList):
                self.particles += p.particles
            else:
                logger.error("Input must be a list of Particle objs or ParticleList objs")
                raise SModelSError
            
        self.particles = sorted(self.particles)
        for p in self.particles:
            for key,val in p.__dict__.items():
                if not hasattr(self, key):
                    setattr(self,key,val)
                elif val != getattr(self,key):
                    setattr(self,key,None)
        
        self.name = label
        
    def __str__(self):
        """
        Returns the ParticleList label (name)
        """
        
        return str(self.name)        
        
    def __cmp__(self,other):
        """
        Compares the list with another list or a single particle.
        :param other: particle list (ParticleList) or single particle (Particle) to be compared
        :return: If other is a single particle, returns:
                    -1 if all particles in self < other, 
                     0 if any particle in self == other,
                    +1, if any particle in self > other.
                If other is a particle list, returns 
                -1 if self < other, 0 if self == other, +1, if self > other.     
        """
        
        if isinstance(other,ParticleList):
            if self.particles != other.particles:
                comp = self.particles > other.particles
                if comp: return 1
                else: return -1 
            else:
                return 0
        
        if isinstance(other,Particle):
            if other in self.particles:
                return 0
            else:
                for p in self.particles:
                    if p > other: return +1
                return -1


