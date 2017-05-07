#!/usr/bin/env python

"""
.. module:: modelParticles
   :synopsis: Defines the particles to be used.
              All particles appearing in the model as well as the SM particles
              must be defined here.
              Only the particles stored in the useParticles list are used by
              external methods.

.. moduleauthor:: Andre Lessa <lessa.a.p@gmail.com>

      
   HOW TO ADD NEW PARTICLES: simply add a new Particle object (or ParticleList) or
   import from another source.
   The only required property for a particle is its zParity and name (or label)
   
   Properties not defined here and defined by the LHE or SLHA input file 
   (such as masses,  width and BRs) are automatically added later.
"""


from smodels.MSSMparticles import MSSM
