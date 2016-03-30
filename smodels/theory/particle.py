#!/usr/bin/env python

"""
.. module:: theory.particle
   :synopsis: Defines the particle class and its methods

.. moduleauthor:: Andre Lessa <lessa.a.p@gmail.com>

"""

import logging
from smodels.theory.exceptions import SModelSTheoryError as SModelSError
logger = logging.getLogger(__name__)


class Particle(object):
    """
    An instance of this class represents a particle.    

    """
    def __init__(self, **kwargs):
        """
        Initializes the particle. Allows for flexible particle properties.
        However, the particle label (name) and Z2-Parity (zParity) MUST always
        be defined.
        
        :parameter name: particle label (string), e.g. W+
        :parameter zParity: Z2-Parity. -1 for odd particles (neutralino, gluino,...)
                                        and +1 for even particles (quarks, Higgs,...)
        """
        if kwargs is None or not 'name' in kwargs:
            logger.error("A name (label) must be defined when creating a particle")
            raise SModelSError
        elif not 'zParity' in kwargs:
            logger.error("The Z2-Parity (zParity) of a particle must always be defined")
            raise SModelSError

        for key,value in kwargs.items():
            setattr(self,key,value)

    
    def __eq__(self,other):
        """
        Checks if the particles are equal. Use as comparison only
        the properties which have been defined for both particles (and are not None).
        Also, protected properties of the type '_property' are not used for comparison.
        """
        
        for key in self.__dict__:
            if self.__dict__[key] is None: continue
            if not key in other.__dict__: continue
            if other.__dict__[key] is None: continue
            if key[0] == '_': continue
            if other.__dict__[key] != self.__dict__[key]:
                return False
        return True
        
        
    def __str__(self):
        """
        String represantion (particle name)
        """
        
        return self.name
    
    def copy(self):
        """
        Generates a copy of the particle  
        """
        
        newP = Particle(name= self.name, zParity = self.zParity)
        for key,val in self.__dict__.items():
            setattr(newP,key,val)
        
        return newP
    
