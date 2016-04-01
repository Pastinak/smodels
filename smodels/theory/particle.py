#!/usr/bin/env python

"""
.. module:: theory.particle
   :synopsis: Defines the particle class, its methods and related functions

.. moduleauthor:: Andre Lessa <lessa.a.p@gmail.com>

"""

import logging
from smodels.theory.exceptions import SModelSTheoryError as SModelSError
from smodels.particleDefinitions import rEven, rOdd, ptcDic
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
                pConjugate.name[-1] = "-"
            elif pConjugate.name[-1] == "-":
                pConjugate.name[-1] = "+"
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
                                     

def getName(pdg):
    """
    Convert pdg number to particle name according to the dictionaries rOdd and
    rEven.

    :type pdg: int
    :returns: particle name (e.g. gluino, mu-, ...)
    
    """
    p = int(pdg)
    if p in rOdd:
        return rOdd[p]
    if p in rEven:
        return rEven[p]
    else:
        return False


def getPdg(name):
    """
    Convert a name to the pdg number according to the dictionaries rOdd and
    rEven.

    :type name: string
    :returns: particle pdg; None, if name could not be resolved
    
    """
    for (pdg, pname) in rOdd.items():
        if name == pname:
            return abs(pdg)
    for (pdg, pname) in rEven.items():
        if name == pname:
            return abs(pdg)
    return None



def simParticles(particles1, particles2, useDict=True):
    """
    Compares two lists of particles. Allows for inclusive
    labels (Ex: L = l, l+ = l, l = l-,...). Ignores particle ordering inside
    the list and particles with no name defined (blank name)
 
    :param particles1: first list of particles (Particle objects)
    :param particles2: second list of particles (Particle objects) 
    :param useDict: use the translation dictionary, i.e. allow e to stand for
                    e+ or e-, l+ to stand for e+ or mu+, etc 
    :returns: True/False if the particles list match (ignoring order)    
    """
    
    plist1 = []
    for p in particles1:
        name = str(p)
        if name: plist1.append(name)
    plist2 = []
    for p in particles2:
        name = str(p)
        if name: plist2.append(name)


    if len(plist1) != len(plist2):
        return False
    for i,p in enumerate(plist1):
        if not isinstance(p,str) or not isinstance(plist2[i],str):
            logger.error("Input must be a list of particle strings")
            raise SModelSError()
        elif not p in ptcDic.keys() + rEven.values():
            logger.error("Unknow particle: %s" %p)
            raise SModelSError()
        elif not plist2[i] in ptcDic.keys() + rEven.values():
            logger.error("Unknow particle: %s" %plist2[i])
            raise SModelSError()
                        
        
    l1 = sorted(plist1)
    l2 = sorted(plist2)
    if not useDict:
        return l1 == l2
    
    #If dictionary is to be used, replace particles by their dictionay entries
    #e.g. [jet,mu+] -> [[q,g,c],[mu+]], [jet,mu] -> [[q,g,c],[mu+,mu-]] 
    extendedL1 = []    
    for i,p in enumerate(plist1):
        if not p in ptcDic:
            extendedL1.append([p])
        else:
            extendedL1.append(ptcDic[p])
    extendedL2 = []    
    for i,p in enumerate(plist2):
        if not p in ptcDic:
            extendedL2.append([p])
        else:
            extendedL2.append(ptcDic[p])
    
    #Generate all combinations of particle lists (already sorted to avoid ordering issues)
    #e.g. [[q,g,c],[mu+]] -> [[q,mu+],[g,mu+],[c,mu+]]
    extendedL1 = [sorted(list(i)) for i in itertools.product(*extendedL1)]
    extendedL2 = [sorted(list(i)) for i in itertools.product(*extendedL2)]

    #Now compare the two lists and see if there is a match:
    for plist in extendedL1:
        if plist in extendedL2: return True
        
    return False

