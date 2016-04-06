#!/usr/bin/env python

"""
.. module:: particles
   :synopsis: Defines the particles to be used.
              All particles appearing in the model as well as the SM particles
              must be defined here.
              Only the particles stored in the useParticles list are used by
              external methods.

.. moduleauthor:: Andre Lessa <lessa.a.p@gmail.com>

      
   HOW TO ADD NEW PARTICLES: simply add a new Particle object (or ParticleList).
   The only required property for a particle is its zParity (R-Parity, KK-Parity,...)
   
   Properties not defined here and defined by the LHE or SLHA input file 
   (such as masses, width and BRs) are automatically added later.
"""

from smodels.theory.particle import Particle
from SMparticleDefinitions import SM
from smodels.tools.physicsUnits import GeV

####  R-odd   ##########
#1st generation squarks and its conjugates:
sdl = Particle(zParity=-1, _name = 'sd_L', _pid = 1000001, qColor = 3, eCharge = -1./3, spin = 0)
sul = Particle(zParity=-1, _name = 'su_L', _pid = 1000002, qColor = 3, eCharge = 2./3, spin = 0)
sdr = Particle(zParity=-1, _name = 'sd_R', _pid = 2000001, qColor = 3, eCharge = -1./3, spin = 0)
sur = Particle(zParity=-1, _name = 'su_R', _pid = 2000002, qColor = 3, eCharge = 2./3, spin = 0)
#2nd generation squarks and its conjugates:
ssl = Particle(zParity=-1, _name = 'ss_L', _pid = 1000003, qColor = 3, eCharge = -1./3, spin = 0)
scl = Particle(zParity=-1, _name = 'sc_L', _pid = 1000004, qColor = 3, eCharge = 2./3, spin = 0)
ssr = Particle(zParity=-1, _name = 'ss_R', _pid = 2000003, qColor = 3, eCharge = -1./3, spin = 0)
scr = Particle(zParity=-1, _name = 'sc_R', _pid = 2000004, qColor = 3, eCharge = 2./3, spin = 0)
#3rd generation squarks and its conjugates:
sb1 = Particle(zParity=-1, _name = 'sb_1', _pid = 1000005, qColor = 3, eCharge = 2./3, spin = 0)
st1 = Particle(zParity=-1, _name = 'st_1', _pid = 1000006, qColor = 3, eCharge = -1./3, spin = 0)
sb2 = Particle(zParity=-1, _name = 'sb_2', _pid = 2000005, qColor = 3, eCharge = 2./3, spin = 0)
st2 = Particle(zParity=-1, _name = 'st_2', _pid = 2000006, qColor = 3, eCharge = -1./3, spin = 0)
#1st generation sleptons and its conjugates:
sel = Particle(zParity=-1, _name = 'se_L', _pid = 1000011, qColor = 0, eCharge = -1, spin = 0)
snel = Particle(zParity=-1, _name = 'sne_L', _pid = 1000012, qColor = 0, eCharge = 0, spin = 0)
ser = Particle(zParity=-1, _name = 'se_R', _pid = 2000011, qColor = 0, eCharge = -1, spin = 0)
#2nd generation sleptons and its conjugates:
smul = Particle(zParity=-1, _name = 'smu_L', _pid = 1000013, qColor = 0, eCharge = -1, spin = 0)
snmul = Particle(zParity=-1, _name = 'snmu_L', _pid = 1000014, qColor = 0, eCharge = 0, spin = 0)
smur = Particle(zParity=-1, _name = 'smu_R', _pid = 2000013, qColor = 0, eCharge = -1, spin = 0)
#3rd generation sleptons and its conjugates:
sta1 = Particle(zParity=-1, _name = 'sta_1', _pid = 1000015, qColor = 0, eCharge = -1, spin = 0)
sntal = Particle(zParity=-1, _name = 'snta_L', _pid = 1000016, qColor = 0, eCharge = 0, spin = 0)
sta2 = Particle(zParity=-1, _name = 'sta_2', _pid = 2000015, qColor = 0, eCharge = -1, spin = 0)
#Gluino:
gluino = Particle(zParity=-1, _name = 'gluino', _pid = 1000021, qColor = 8, eCharge = 0, spin = 1./2)
#Neutralinos
n1 = Particle(zParity=-1, _name = 'N1', _pid = 1000022, qColor = 0, eCharge = 0, spin = 1./2)
n2 = Particle(zParity=-1, _name = 'N2', _pid = 1000023, qColor = 0, eCharge = 0, spin = 1./2)
n3 = Particle(zParity=-1, _name = 'N3', _pid = 1000025, qColor = 0, eCharge = 0, spin = 1./2)
n4 = Particle(zParity=-1, _name = 'N4', _pid = 1000035, qColor = 0, eCharge = 0, spin = 1./2)
#Charginos
c1 = Particle(zParity=-1, _name = 'C1+', _pid = 1000024, qColor = 0, eCharge = 1, spin = 1./2)
c2 = Particle(zParity=-1, _name = 'C2+', _pid = 1000037, qColor = 0, eCharge = 1, spin = 1./2)

##### R-even  ###############
#Higgs
H = Particle(zParity=-1, _name = 'H+', _pid = 37, qColor = 0, eCharge = +1, spin = 0)
A0 = Particle(zParity=-1, _name = 'A0', _pid = 36, qColor = 0, eCharge = 0, spin = 0)
H0 = Particle(zParity=-1, _name = 'H0', _pid = 35, qColor = 0, eCharge = 0, spin = 0)


squarks = [sdl,sul,sdr,sur] + [ssl,scl,ssr,scr] + [sb1,st1,sb2,st2]
sleptons = [sel,snel,ser] + [smul,snmul,smur] + [sta1,sntal,sta2]
inos = [gluino] + [n1,n2,n3,n4] + [c1,c2]
higgs = [H,A0,H0]
#R-even particles should be treated as stable to preserve topology structures
for p in higgs: p.width = 0.*GeV

sparticles = squarks + sleptons + inos + higgs
sparticlesC = [p.chargeConjugate() for p in sparticles]  #Define the charge conjugates
MSSM = SM + sparticles + sparticlesC

