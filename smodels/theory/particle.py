#!/usr/bin/env python

"""
.. module:: theory.particle
   :synopsis: Defines the particle class, its methods and related functions

.. moduleauthor:: Andre Lessa <lessa.a.p@gmail.com>

"""

import logging
from smodels.theory.exceptions import SModelSTheoryError as SModelSError
from smodels.tools.physicsUnits import GeV
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
            self.addProperty(key,value)

    
    def __cmp__(self,other):
        """
        Compares the particle with other.
        Only compares physics attributes/properties (ignore properties starting with "_",
        such as _pid).
        First compare masses (if it exists) then other properties.
        If other is a ParticleList, uses the ParticleList comparison method.
        :param other:  particle to be compared (Particle object)
        :return: -1 if self < other, 0 if self == other, +1, if self > other.        
        """
        
        if not isinstance(other,ParticleList) and not isinstance(other,Particle):
            return +1
        
        if isinstance(other,ParticleList):
            return other.__cmp__(self)
        
        if self.zParity != other.zParity:
            comp = self.zParity > other.zParity
            if comp: return 1
            else: return -1            
        
        if hasattr(self,'mass') and hasattr(other,'mass'):
            if self.mass != other.mass:
                comp = self.mass > other.mass
                if comp: return 1
                else: return -1
        for key,val in sorted(self.__dict__.items()):
            if key[0] == '_': continue  #Skip non-physical properties
            if val is None: continue
            if not key in other.__dict__: continue
            if other.__dict__[key] is None: continue            
            if other.__dict__[key] != val:
                comp = val > other.__dict__[key]
                if comp: return 1
                else: return -1                    
        
        return 0 #Particles are equal
        
        
    def __str__(self):
        """
        String represantion (particle name, if defined)
        :return: Particle name, if defined. Otherwise empty string.
        """
        if hasattr(self, '_name'):
            return self._name
        else:
            return ''
    
    def copy(self,relevantProp=None):
        """
        Generates a copy of the particle
        :param relevantProp: List of the relevant properties to be kept in the copy 
                            (e.g. ['_name','mass','eCharge',...])
                            If None, keep all properties.
        :return: copy of itself (Particle object)
        """
        
        newP = Particle(zParity = self.zParity)
        for key,val in self.__dict__.items():
            if relevantProp is None or key in relevantProp:
                newP.addProperty(key,val)
        
        return newP
    
    def addProperty(self,label,value,overwrite=False):
        """
        Add property with label and value.
        If overwrite = False and property already exists, it will not be overwritten
        :parameter label: property label (e.g. "mass", "_name",...)
        :parameter value: property value (e.g. 171*GeV, "t+",...)
        """
        
        if overwrite:
            setattr(self, label, value)
        elif not hasattr(self, label) or getattr(self, label) is None:
            setattr(self, label, value)
    
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
        if hasattr(pConjugate, '_name'):
            if pConjugate._name[-1] == "+":
                pConjugate._name = pConjugate._name[:-1] + "-"
            elif pConjugate._name[-1] == "-":
                pConjugate._name = pConjugate._name[:-1] + "+"
            else:
                pConjugate._name += "*"
                
        return pConjugate
    
    def isStable(self):
        """
        Return True if particle is stable, false otherwise.
        A particle is considered stable if it has zero width or if
        the width has not been defined
        :return: True/False
        """
        
        if not hasattr(self, '_width'):
            return True
        elif type(self._width) == type(1.*GeV) and self._width > 0.*GeV:
            return False
        else:
            return True
        
    def isInvisible(self):
        """
        Return True if particle is invisible, false otherwise.
        A particle is considered invisible if it has zero eCharge,
        zero qCharge and it is not a photon (_pid = 22).
        the width has not been defined.
        If eCharge or qColor have not been defined, return False
        :return: True/False
        """
        
        if not hasattr(self, 'eCharge') or not hasattr(self, 'qColor'):
            return False
        elif self.eCharge != 0 or self.qColor != 0:
            return False
        elif hasattr(self,'_pid') and self._pid == 22:
            return False
        else:
            return True        
    
    
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
                elif getattr(self,key) is None:  #Attribute has already been set to None (skip)
                    continue 
                elif val != getattr(self,key):
                    setattr(self,key,None)
        
        self._name = label
        
    def __str__(self):
        """
        Returns the ParticleList label (name)
        """
        
        return str(self._name)        
        
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
