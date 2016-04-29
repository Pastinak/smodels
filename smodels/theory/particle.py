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
        If the _internalID property exists for both objects, use it as comparison,
        otherwise compares physics attributes/properties (ignore properties starting with "_",
        such as _pid, _name,...).
        First compare zParity, then compare masses (if it exists), then other properties.
        If other is a ParticleList, uses the ParticleList comparison method.
        :param other:  particle to be compared (Particle object)
        :return: -1 if self < other, 0 if self == other, +1, if self > other.        
        """
        
        if not isinstance(other,ParticleList) and not isinstance(other,Particle):
            return +1
        
        #Use _internalID, if defined for both particles or particle lists
        if hasattr(self,'_internalID') and self._internalID:
            if hasattr(other,'_internalID') and other._internalID:
                if self._internalID.intersection(other._internalID):
                    return 0
                else:
                    comp = max(self._internalID) > max(other._internalID)
                    if comp: return 1
                    else: return -1

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
            
            
    def combineWith(self,other):
        """
        Combines the particle with another particle or with a list.
        If the particles are the same, return self.
        Otherwise return a particle list
        :parameter other: a Particle or ParticleList object
        :return: a Particle or ParticleList object containing other
        """
        
        if isinstance(other,ParticleList):
            return other.combineWith(self)
        elif(other,Particle):
            if other is self:
                return self
            else:
                return ParticleList(particles=[self,other])
        else:
            logger.error("Input should be a Particle or ParticleList object.")
            
            
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

    def __init__(self, particles, label=None):
        """
        Initializes the particle list. Particles can be a list of Particle objects
        and/or ParticleList objects. For the later all the particles in the ParticleList
        are included.
        All the common (shared) properties for all particles in the list are automatically
        attributed to the ParticleList. Properties which are not shared by all the particles
        are set to None, except for the _internalID attribute, which is combined.
        The ParticleList name is set to label.
        :param particles: list of single particles or ParticleLists
        :param label: name of the list
        :param internalID: internalID for the list (set object). If defined, should be a set
                           containing the internalIDs of its particles.
        """
                
        self.particles = []
        internalIDs = []
        for p in particles:
            if isinstance(p,Particle):
                self.particles.append(p)
            elif isinstance(p,ParticleList):
                self.particles += p.particles
            else:
                logger.error("Input must be a list of Particle objs or ParticleList objs")
                raise SModelSError
            if hasattr(p,'_internalID'):
                internalIDs += list(p._internalID)

            
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
        if internalIDs:
            self._internalID = set(internalIDs)
        
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
        
        #Use _internalID, if defined for both particles or particle lists
        if hasattr(self,'_internalID') and self._internalID:
            if hasattr(other,'_internalID') and other._internalID:
                if self._internalID.intersection(other._internalID):
                    return 0
                else:
                    comp = max(self._internalID) > max(other._internalID)
                    if comp: return 1
                    else: return -1
        
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
            
    def combineWith(self,other):
        """
        Combines the list with another list or with a particle.
        If the lists contain exactly the same particles or if the particle
        to be added already appears in self, return self.
        :parameter other: a Particle or ParticleList object
        :return: a ParticleList object containing other
        """
        
        newparticles = []
        if isinstance(other,Particle):
            for p in self.particles:
                if other is p: return self  #Particle already appears in list            
            newparticles = self.particles[:] + [other] #Include particle in list
            
        elif isinstance(other,ParticleList):
            if len(other.particles) == len(self.particles):
                for ip,p in self.particles:
                    if other.particles[ip] is p:
                        continue
                    else:
                        newparticles.append(other.particles[ip])
        
            if not newparticles:
                return self  #Lists are equal
            else:
                newparticles += self.particles
        
        newparticles = list(set(newparticles))
        newList = ParticleList(particles=newparticles)
        return newList


def setInternalID(particlesList):
    """
    Attributes an internal ID property for each particle to be used
    when comparing two particles, so the full comparison does not have to
    be performed each time. This function should only be used when no further
    changes will be made to the particles.
    :parameter particlesList: a list of Particle or ParticleList objects
    """
    
    if not isinstance(particlesList,list):
        logger.error("The input must be a list.")
        raise SModelSError()        
    for p in particlesList:
        if not isinstance(p,Particle) and not isinstance(p,ParticleList):
            logger.error("The input must be a list of Particle or ParticleList objects")
            raise SModelSError()
        
    #First split list into Particle and ParticleList objects:    
    particles = sorted([p for p in particlesList if isinstance(p,Particle)])
    plists = sorted([p for p in particlesList if isinstance(p,ParticleList)])
    
    #Compare all particles and store results:
    comps = []
    for ip,p in enumerate(particles):
        #Reset internal ID properties
        p._internalID = None
        comps.append([p.__cmp__(pB) for pB in particles])
    #Now assign integer IDs to single particles:
    pID = 0
    for ip,p in enumerate(particles):
        if not p._internalID is None: continue #ID has already been set, continue
        pID += 1
        p._internalID = set([pID])
        for jp,c in enumerate(comps[ip]):
            if c == 0: #Particles match
                particles[jp]._internalID = p._internalID
   
    #Now assign IDs to particle lists:
    for pL in plists:
        pL._internalID = None
        matchingIDs = []
        for p in particles:
            if p == pL:
                matchingIDs += list(p._internalID)
        pL._internalID = set(matchingIDs)
