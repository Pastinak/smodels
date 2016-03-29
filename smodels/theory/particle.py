#!/usr/bin/env python

"""
.. module:: theory.particle
   :synopsis: Defines the particle class and its methods

.. moduleauthor:: Andre Lessa <lessa.a.p@gmail.com>

"""

import unum
import logging
from smodels.theory.exceptions import SModelSTheoryError as SModelSError
logger = logging.getLogger(__name__)


class Particle(object):
    """
    An instance of this class represents a particle.    

    """
    def __init__(self, name=None, pid=None, mass=None, spin=None,
                  eCharge=None, qColor=None, zParity=None):
        """
        Initializes the particle.
        
        :parameter name: particle label (string), e.g. W+
        :parameter pid: particle PID, e.g. 15
        :parameter mass: particle mass, e.g. 100.*GeV 
        :parameter spin: particle spin, e.g. 0, 1/2,...
        :parameter eCharge: electric charge, e.g. -1,+1,...
        :parameter qColor: dimension of color representation, e.g. 1 (singlet), 3 (triplet), 8,...
        :parameter zParity: Z2-Parity. -1 for odd particles (neutralino, gluino,...)
                                        and +1 for even particles (quarks, Higgs,...)
        """
        
        if not isinstance(name,str):
            logger.error("Particle name must be a string and not %s" %str(type(name)))
            raise SModelSError
        else:
            self.name = name
        if not isinstance(pid,int):
            logger.error("Particle PID must be an integer and not %s" %str(type(pid)))
            raise SModelSError
        else:
            self.pid = pid
        if not isinstance(mass,unum.Unum):
            logger.error("Particle mass must be a Unum object (e.g. 100*GeV) and not %s" %str(type(mass)))
            raise SModelSError
        else:          
            self.mass = mass
        if not isinstance(spin,float) and not isinstance(spin,int):
            logger.error("Particle spin must be an integer or float and not %s" %str(type(spin)))
            raise SModelSError
        else:            
            self.spin = float(spin)
        if not isinstance(eCharge,float) and not isinstance(eCharge,int):
            logger.error("Particle eCharge must be an integer or float and not %s" %str(type(eCharge)))
            raise SModelSError
        else:            
            self.eCharge = float(eCharge)            
        if not isinstance(qColor,int):
            logger.error("Particle qColor must be an integer and not %s" %str(type(qColor)))
            raise SModelSError
        else:            
            self.qColor = qColor             
        if zParity != 1 and zParity != -1:
            logger.error("Particle zParity must be +1 or -1")
            raise SModelSError
        else:            
            self.zParity = zParity
        
    def __eq__(self,other):
        """
        Checks if the particles are equal. Use as comparison only
        the properties which have been defined for both particles (and are not None).
        """
        
        for key in self.__dict__:
            if self.__dict__[key] is None: continue
            if not key in other.__dict__: continue
            if other.__dict__[key] is None: continue
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
        
        newP = Particle()
        newP.name = self.name
        newP.mass = self.mass
        newP.pid = self.pid
        newP.spin = self.spin
        newP.eCharge = self.eCharge
        newP.qColor = self.qColor
        newP.zParity = self.zParity
        
        return newP
