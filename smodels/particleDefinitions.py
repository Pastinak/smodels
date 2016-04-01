#!/usr/bin/env python

"""
.. module:: particles
   :synopsis: Defines the particles to be used.
              All particles appearing in the model as well as the SM particles
              must be defined (or imported) here.
              Only the particles stored in the useParticles list are used by
              external methods.

.. moduleauthor:: Andre Lessa <lessa.a.p@gmail.com>

      
   HOW TO ADD NEW PARTICLES: simply add a new Particle object (or ParticleList).
   The only required property for a particle is its zParity (R-Parity, KK-Parity,...)
   
   Properties defined by the LHE or SLHA input file (such as masses, width and BRs)
   are automatically added later.
"""

from MSSMparticleDefinitions import MSSM
from smodels.theory.particle import Particle


useParticles = MSSM


#Add new particle:
#new = Particle(name='some_new_particle', _pid=1000, eCharge = 0, qColor = 3, spin = 0)
#useParticles = MSSM + [new]
