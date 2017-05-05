"""
.. module:: particle
   :synopsis: Module holding the Particle class and its methods.
    
.. moduleauthor:: Andre Lessa <lessa.a.p@gmail.com>
    
"""

from smodels.modelParticles import particleList
from smodels.tools.smodelsLogging import logger
from smodels.theory.exceptions import SModelSTheoryError as SModelSError


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
    
    def __init__(self, particleStr=None):
        """
        Initializes the particle from the . If particleStr is defined, returns
        the corresponding particle using the pre-defined model particles
        
        :parameter particleStr: string describing the particle (e.g. e+, L,...)
        """
        
        self.mass = None
        self.width = None
        self.eCharge = None
        self.cCharge = None
        self.spin = None
        self.name = particleStr
                    
        if isinstance(particleStr,str):
            return self.fromString(particleStr)
        elif particleStr:
            logger.error("Invalid argument type: %s" %type(particleStr))
            raise SModelSError()
    
    def fromString(self,particleStr):
        """
        Returns the particle from the particle list defined in modelParticles.
        If the particle does not exist, will raise an error
        
        :param particleStr: string representing one of pre-defined particles.
        """
        
        for ptc in modelParticles
        
            
    def __str__(self):
        return self.name