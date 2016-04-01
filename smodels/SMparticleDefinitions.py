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
   
   Properties defined by the LHE or SLHA input file (such as masses, width and BRs)
   are automatically added later.
"""

from smodels.theory.particle import Particle, ParticleList

#1st generation quarks
d = Particle(zParity=+1, name = 'q', _pid = 1, qColor = 3, eCharge = -1/3, spin = 1/2)
u = Particle(zParity=+1, name = 'q', _pid = 2, qColor = 3, eCharge = 2/3, spin = 1/2)
#2nd generation quarks
s = Particle(zParity=+1, name = 'q', _pid = 3, qColor = 3, eCharge = -1/3, spin = 1/2)
c = Particle(zParity=+1, name = 'c', _pid = 4, qColor = 3, eCharge = 2/3, spin = 1/2)
#3rd generation quarks
b = Particle(zParity=+1, name = 'b', _pid = 5, qColor = 3, eCharge = -1/3, spin = 1/2)
t = Particle(zParity=+1, name = 't+', _pid = 6, qColor = 3, eCharge = 2/3, spin = 1/2)
#1st generation leptons
e = Particle(zParity=+1, name = 'e-', _pid = 11, qColor = 0, eCharge = -1, spin = 1/2)
ne = Particle(zParity=+1, name = 'nu', _pid = 12, qColor = 0, eCharge = 0, spin = 1/2)
#2nd generation leptons
mu = Particle(zParity=+1, name = 'mu-', _pid = 13, qColor = 0, eCharge = -1, spin = 1/2)
nmu = Particle(zParity=+1, name = 'nu', _pid = 14, qColor = 0, eCharge = 0, spin = 1/2)
#3rd generation leptons
ta = Particle(zParity=+1, name = 'ta-', _pid = 15, qColor = 0, eCharge = -1, spin = 1/2)
nta = Particle(zParity=+1, name = 'nu', _pid = 16, qColor = 0, eCharge = 0, spin = 1/2)
#Gauge bosons:
gluon = Particle(zParity=+1, name = 'g', _pid = 21, qColor = 3, eCharge = 0, spin = 1)
photon = Particle(zParity=+1, name = 'photon', _pid = 22, qColor = 0, eCharge = 0, spin = 1)
Z = Particle(zParity=+1, name = 'Z', _pid = 23, qColor = 0, eCharge = 0, spin = 1)
W = Particle(zParity=+1, name = 'W+', _pid = 24, qColor = 0, eCharge = +1, spin = 1)
#SM Higgs
higgs = Particle(zParity=1, name = 'higgs', _pid = 25, qColor = 0, eCharge = 0, spin = 0)

quarks = [u,d] + [c,s] + [t,b]
quarksC = [p.chargeConjugate() for p in quarks]
leptons = [e,ne] + [mu,nmu] + [ta,nta]
leptonsC = [p.chargeConjugate() for p in leptons]
gauge = [gluon,photon,W,Z]
gaugeC = [p.chargeConjugate() for p in gauge]
SMparticles = quarks + leptons + gauge + [higgs]
SMparticlesC = quarksC + leptonsC + gaugeC + [higgs.chargeConjugate()]

SM = SMparticles + SMparticlesC


#Inlcusive labels
eList = ParticleList(particles=[leptons[0],leptonsC[0]],label='e')
muList = ParticleList(particles=[leptons[2],leptonsC[2]],label='mu')
taList = ParticleList(particles=[leptons[4],leptonsC[4]],label='ta')
lpList = ParticleList(particles=[leptonsC[0],leptonsC[2]],label='l+')
lmList = ParticleList(particles=[leptons[0],leptons[2]],label='l-')
lList = ParticleList(particles=[lpList,lmList],label='l')
WList = ParticleList(particles=[gauge[2],gaugeC[2]],label='W')
tList = ParticleList(particles=[quarks[4],quarksC[4]],label='t')
LpList = ParticleList(particles=[lpList,leptonsC[4]],label='L+')
LmList = ParticleList(particles=[lmList,leptons[4]],label='L-')
LList = ParticleList(particles=[LpList,LmList],label='L')
jetList = ParticleList(particles=[quarks[0:4],quarksC[0:4],gauge[0],gaugeC[0]],label='jet')
allp = ParticleList(particles=SMparticles,label='all')
