"""
.. module:: particle
   :synopsis: Module holding the Particle class and its methods.
    
.. moduleauthor:: Andre Lessa <lessa.a.p@gmail.com>
    
"""

from smodels.modelParticles import particleList
from smodels.tools.smodelsLogging import logger
from smodels.theory.exceptions import SModelSTheoryError as SModelSError


requiredAttr = ['zParity','name']

class Particle(object):
    """
    An instance of this class represents a particle.    
    This class possesses several attributes (mass,qNumbers,width,zparity,...)
    
    :ivar mass: mass of the particle
    :ivar width: width of the particle
    :ivar eCharge: eletric charge
    :ivar cCharge: color charge
    :ivar spin: spin
    :ivar name: string representation for the particle    
    """
    
    def __init__(self, **particleAtt):
        """
        Initializes the particle from the . If particleStr is defined, returns
        the corresponding particle using the pre-defined model particles
        
        :parameter particleStr: string describing the particle (e.g. e+, L,...)
        """
        
        for key,val in particleAtt.items():
            setattr(self,key,val)
        
        for rAtt in requiredAttr:
            if not rAtt in particleAtt:
                logger.error("Particle must have %s attribute" %rAtt)
                raise SModelSError()
    
    def fromString(self,particleStr):
        """
        Returns the particle from the particle list defined in modelParticles.
        If the particle does not exist, will raise an error
        
        :param particleStr: string representing one of pre-defined particles.
        """
        
        if not isinstance(particleStr,str):
            logger.error("Input must be a string.")
            raise SModelSError()
        
        for ptc in modelParticles:
            if str(ptc) == particleStr:
                return ptc
        
        logger.error("Particle %s not defined. Please add it to model particles." %particleStr)
        raise SModelSError()    
    
    def __cmp__(self,other):
        """
        Compares the particle with other.        
        The comparison is made based on the particle name.         
        :param other:  particle to be compared (Particle object)
        :return: -1 if self < other, 0 if self == other, +1, if self > other.
        """
        
        if not isinstance(other,Particle):
            logger.warning("Comparing particle object with %s" %str(type(other)))
            return 1
    
        return self.name.__cmp__(other.name)
            
    def __str__(self):
        return self.name