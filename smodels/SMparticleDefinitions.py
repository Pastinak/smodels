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
   The only required property for a particle is its zParity (R-Parity,KK-Parity,...)
   
   Non-physical properties,such as the PDG id,should
   start with "_" (e.g. _pid) are not used when comparing two particles.
   
   Properties not defined here and defined by the LHE or SLHA input file 
   (such as masses, width and BRs) are automatically added later.
"""

from smodels.theory.particle import Particle,ParticleList
from smodels.tools.physicsUnits import GeV

#1st generation quarks
d = Particle(zParity=+1,_name = 'd',_pid = 1,qColor = 3,eCharge = -1./3,spin = 1./2,mass = 0.*GeV)
u = Particle(zParity=+1,_name = 'u',_pid = 2,qColor = 3,eCharge = 2./3,spin = 1./2,mass = 0.*GeV)
#2nd generation quarks
s = Particle(zParity=+1,_name = 's',_pid = 3,qColor = 3,eCharge = -1./3,spin = 1./2,mass = 0.*GeV)
c = Particle(zParity=+1,_name = 'c',_pid = 4,qColor = 3,eCharge = 2./3,spin = 1./2,mass = 1.275*GeV)
#3rd generation quarks
b = Particle(zParity=+1,_name = 'b-',_pid = 5,qColor = 3,eCharge = -1./3,spin = 1./2,mass = 4.66*GeV)
t = Particle(zParity=+1,_name = 't+',_pid = 6,qColor = 3,eCharge = 2./3,spin = 1./2,mass = 173.21*GeV)
#1st generation leptons
e = Particle(zParity=+1,_name = 'e-',_pid = 11,qColor = 0,eCharge = -1,spin = 1./2, mass = 0.*GeV)
ne = Particle(zParity=+1,_name = 'nue',_pid = 12,qColor = 0,eCharge = 0,spin = 1./2, mass = 0.*GeV)
#2nd generation leptons
mu = Particle(zParity=+1,_name = 'mu-',_pid = 13,qColor = 0,eCharge = -1,spin = 1./2, mass = 0.106*GeV)
nmu = Particle(zParity=+1,_name = 'numu',_pid = 14,qColor = 0,eCharge = 0,spin = 1./2, mass = 0.*GeV)
#3rd generation leptons
ta = Particle(zParity=+1,_name = 'ta-',_pid = 15,qColor = 0,eCharge = -1,spin = 1./2, mass = 1.77*GeV)
nta = Particle(zParity=+1,_name = 'nuta',_pid = 16,qColor = 0,eCharge = 0,spin = 1./2, mass = 0.*GeV)
#Gauge bosons:
gluon = Particle(zParity=+1,_name = 'g',_pid = 21,qColor = 3,eCharge = 0,spin = 1, mass = 0.*GeV)
photon = Particle(zParity=+1,_name = 'photon',_pid = 22,qColor = 0,eCharge = 0,spin = 1, mass = 0.*GeV)
Z = Particle(zParity=+1,_name = 'Z',_pid = 23,qColor = 0,eCharge = 0,spin = 1, mass = 91.2*GeV)
W = Particle(zParity=+1,_name = 'W+',_pid = 24,qColor = 0,eCharge = +1,spin = 1, mass = 80.4*GeV)
#SM Higgs
higgs = Particle(zParity=1,_name = 'higgs',_pid = 25,qColor = 0,eCharge = 0,spin = 0, mass = 125.*GeV)

quarks = [u,d] + [c,s] + [t,b]
quarksC = [p.chargeConjugate() for p in quarks]
leptons = [e,ne] + [mu,nmu] + [ta,nta]
leptonsC = [p.chargeConjugate() for p in leptons]
gauge = [gluon,photon,W,Z]
gaugeC = [p.chargeConjugate() for p in gauge]
SMparticles = quarks + leptons + gauge + [higgs]
SMparticlesC = quarksC + leptonsC + gaugeC + [higgs.chargeConjugate()]

SM = SMparticles + SMparticlesC
#Define all SM particles as stable 
#(even parity states should be treated as stable to preserve topology structures):
for p in SM: p._width = 0.*GeV


#Inlcusive labels
eList = ParticleList(particles=[leptons[0],leptonsC[0]],label='e')
muList = ParticleList(particles=[leptons[2],leptonsC[2]],label='mu')
taList = ParticleList(particles=[leptons[4],leptonsC[4]],label='ta')
lpList = ParticleList(particles=[leptonsC[0],leptonsC[2]],label='l+')
lmList = ParticleList(particles=[leptons[0],leptons[2]],label='l-')
lList = ParticleList(particles=[lpList,lmList],label='l')
WList = ParticleList(particles=[gauge[2],gaugeC[2]],label='W')
tList = ParticleList(particles=[quarks[4],quarksC[4]],label='t')
bList = ParticleList(particles=[quarks[5],quarksC[5]],label='b')
LpList = ParticleList(particles=[lpList,leptonsC[4]],label='L+')
LmList = ParticleList(particles=[lmList,leptons[4]],label='L-')
LList = ParticleList(particles=[LpList,LmList],label='L')
jetList = ParticleList(particles= quarks[0:4]+quarksC[0:4]+[gauge[0],gaugeC[0]],label='jet')
allp = ParticleList(particles=SMparticles,label='all')

particleLists = [eList, muList,taList,lpList,lmList,lList,WList,tList,bList,
                 LpList,LmList,LList,jetList,allp]

SM += particleLists
