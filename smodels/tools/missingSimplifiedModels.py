#!/usr/bin/env python3

"""
.. module: missingSimplifiedModels
   :synopsis: From missing PIDs and missing topologies
              build a missing simplified modellist.

.. moduleauthor:: Jory Sonneveld <jory@opmijnfiets.nl>

"""

#from smodels.tools import missingTopologies
from smodels.tools import tdict
#import unum
#from smodels.tools.physicsUnits import GeV
from physicsUnits import GeV, pb
from math import floor, log10
from smodels.tools import txNames
from smodels.tools import txDecays
#from smodels_utils.helper import txNames
#from smodels_utils.helper import txDecays
from smodels import particles


def round_to_sign(x, sig=3):
    """
    Round the given number to the significant number of digits.
    """
    rounding = sig - int(floor(log10(x))) - 1
    if rounding == 0:
        return int(x)
    else:
        return round(x, rounding)

def sms_name(elem):
    """
    """

    tx = txNames.getTx(elem)
    finalstate = elem.getParticles()
    #print(tx, pids, parts)
    decays = txDecays.decays
    #txes = {'T2': 'signature': "[[[jet]],[[jet]]]", 'particles': "[[[1000002, 1000022], [1000021, 1000022]]]"}
    #{'T2': 'signature': "[[[jet]],[[jet]]]", 'particles': "[[[1000002, 1000022], [1000021, 1000022]]]"}
    if str(finalstate) in tdict.tdict:
        return tdict.tdict[str(finalstate)]
    else:
        return None


def missing_elem_list(missing_elements, mistop_sqrts):
    """
    Given a bunch of elements, aggregate them into a list
    (ordered by weight) ignoring antiparticles and order,
    and group for like masses.
    """
    missing_elts = []
    elementdict = {}
    for elem in missing_elements[:10]:
        pids = elem.getPIDs()

        # We do not keep track of antiparticles:
        pids_no_minus = str(pids).replace('-', '')

        # Get the cross section * branching ratio:
        wt = elem.weight.getXsecsFor(mistop_sqrts)[0].value

        # Get the particle names (final state):
        parts = elem.getParticles()
        # Get the particle masses:
        masses = elem.getMasses()
        # Keep track of only unique particles for each branch.
        # Again, here the antiparticles are ignored:
        branches = unique_particles(pids, parts, masses)

        tx = sms_name(elem)

        # Add weight if it only concerns antiparticles:
        if pids_no_minus in elementdict:
            elementdict[pids_no_minus]['ELweightPB'] += wt.asNumber(pb)
        # Add new element otherwise:
        else:
            elt = {'pids': str(pids_no_minus),
                    'ELweightPB': wt.asNumber(pb),
                    'branch': branches, 'txname': tx}
            elementdict[pids_no_minus] = elt
    for elt in sorted(elementdict.values(), key=lambda x: x['ELweightPB'], reverse=True):
        missing_elts.append(elt)
    return missing_elts


def missing_sms_dict(missing_topos, sqrts):
    """(MissingTopos)-> [list]

    Given a missing topology, which can be quite general
    in the sense that it only gives a certain final state,
    return the specific particle IDs and weights of what can
    be called missing simplified models.

    >>> 
    """
    mistop_sqrts = sqrts
    missing_topo_dict = {'topology': []}
    #missing_topos = {uncovered.missingTopos.topos: 'missing'}
    #missing_topos.update({uncovered.outsideGrid.topos: 'outsideGrid'})
    # missing_topos.update({uncovered.longCascade.topos: 'longCascade'})
    # missing_topos.update({uncovered.asymmetricBranches.topos: 'asymmetricBranches'})
    for mistop in sorted(missing_topos.topos, key=lambda x: x.value, reverse=True):
        topname = mistop.topo

        topweight = 0
        for el in mistop.contributingElements:
            if not el.weight.getXsecsFor(mistop_sqrts): continue
            topweight += el.weight.getXsecsFor(mistop_sqrts)[0].value.asNumber(pb)
        missing = {'name': topname, 'TOPweightPB': topweight, 'sqrts': str(mistop_sqrts)}
        missing['elem'] = missing_elem_list(mistop.contributingElements, mistop_sqrts)
        missing_topo_dict['topology'].append(missing)

    missing_topo_dict['topology'].sort(key=lambda x: x['TOPweightPB'], reverse=True)
    #print("returning missing sms dict")
    return missing_topo_dict



#def missing_sms_dict(missing_topos):
#    """(MissingTopo)-> [list]
#
#    Given a missing topology, which can be quite general
#    in the sense that it only gives a certain final state,
#    return the specific particle IDs and weights of what can
#    be called missing simplified models.
#
#    >>> 
#    """
#    missing_topo_dict = {'topology': []}
#    mistop_sqrts = missing_topos.sqrts
#    for mistop in sorted(missing_topos.topos, key=lambda x: x.value, reverse=True):
#        topname = mistop.topo
#        topweight = mistop.weights.getXsecsFor(mistop_sqrts)[0].value.asNumber(pb)
#        missing = {'name': topname, 'TOPweightPB': topweight, 'sqrts': str(mistop_sqrts)}
#        missing['elem'] = []
#        elementdict = {}
#        for elem in mistop.contributingElements:
#            pids = elem.getPIDs()
#
#            # We do not keep track of antiparticles:
#            pids_no_minus = str(pids).replace('-', '')
#
#            # Get the cross section * branching ratio:
#            wt = elem.weight.getXsecsFor(mistop_sqrts)[0].value
#            # Get the particle names (final state):
#            parts = elem.getParticles()
#            # Get the particle masses:
#            masses = elem.getMasses()
#            # Keep track of only unique particles for each branch.
#            # Again, here the antiparticles are ignored:
#            branches = unique_particles(pids, parts, masses)
#
#            # Add weight if it only concerns antiparticles:
#            if pids_no_minus in elementdict:
#                elementdict[pids_no_minus]['ELweightPB'] += wt.asNumber(pb)
#            # Add new element otherwise:
#            else:
#                elt = {'pids': str(pids_no_minus),
#                        'ELweightPB': wt.asNumber(pb),
#                        'branch': branches}
#                elementdict[pids_no_minus] = elt
#        for elt in sorted(elementdict.values(), key=lambda x: x['ELweightPB'], reverse=True):
#            missing['elem'].append(elt)
#        missing_topo_dict['topology'].append(missing)
#
#    return missing_topo_dict




def unique_particles(pids, final_states, masses):
    """([int], [str], [unum.Unum]) -> list of dicts
    Given the masses, final state particles and pids
    of a certain element, build a dictionary for each
    branch with the unique particles per mass.

    >>> pids = [[[1000002, 1000024, 1000022], [1000002, 1000024, -1000022]],\
               [[1000002, 1000024, 1000022], [1000004, 1000024, 1000022]],\
               [[1000002, 1000024, 1000022], [1000002, 1000024, 1000022]],\
               [[1000002, 1000024, 1000022], [1000004, 1000024, 1000022]]]
    >>> masses = [[9.92E+02*GeV, 2.69E+02*GeV, 1.29E+02*GeV], [9.92E+02*GeV,\
               2.69E+02*GeV, 1.29E+02*GeV]]
    >>> print(masses)
    [[9.92E+02 [GeV], 2.69E+02 [GeV], 1.29E+02 [GeV]], [9.92E+02 [GeV], 2.69E+02 [GeV], 1.29E+02 [GeV]]]
    >>> final_states = [[['q'], ['W+']], [['q'], ['W+']]]
    >>> unique_particles(pids, final_states, masses)
    [{'finalstate': [['q'], ['W']], 'particles': [{'massGeV': 992, 'pid':
        [1000002]}, {'massGeV': 269, 'pid': [1000024]}, {'massGeV': 129, 'pid':
            [1000022]}]}, {'finalstate': [['q'], ['W']], 'particles':
                [{'massGeV': 992, 'pid': [1000002, 1000004]}, {'massGeV':  269,
                    'pid': [1000024]}, {'massGeV': 129, 'pid': [1000022]}]}]


    """
    branches = []

    for branchno in range(len(final_states)):
        branchname = str(final_states[branchno]).replace('-', '').replace('+',
                '')
        particles = []
        for particlemassno in range(len(masses[branchno])):
            particlemass = masses[branchno][particlemassno]
            massGeV = round_to_sign(particlemass.asNumber(GeV), 3)
            degenerate_particles = []
            for degenerates in pids:
                particle = abs(degenerates[branchno][particlemassno])
                if particle not in degenerate_particles:
                    degenerate_particles.append(particle)
            particles.append({'massGeV': massGeV, 'pid':
                degenerate_particles})
        branches.append({'finalstate': branchname, 'particle':
                particles})
    return branches



    """
            <topology>
                <sqrts>8.00E+00 [TeV]</sqrts>
                <TOPweightPB>0.00642879439972</TOPweightPB>
                <name>[[[q],[W]],[[q],[W]]]</name>
                <elem_list>
                    <elem>
                        <pids>[[[1000002, 1000024, 1000022], [1000002, 1000024, 1000022]], [[1000002, 1000024, 1000022], [1000004, 1000024, 1000022]], [[1000002, 1000024, 1000022], [1000002, 1000024, 1000022]], [[1000002, 1000024, 1000022], [1000004, 1000024, 1000022]]]</pids>
                        <parts>[[['q'], ['W+']], [['q'], ['W+']]]</parts>
                        <masses>[[9.92E+02 [GeV], 2.69E+02 [GeV], 1.29E+02 [GeV]], [9.92E+02 [GeV], 2.69E+02 [GeV], 1.29E+02 [GeV]]]</masses>
                        <ELweightPB>0.00316270903106</ELweightPB>
                    </elem>
                    <elem>
                        <pids>[[[1000002, 1000024, 1000022], [1000001, 1000024, 1000022]]]</pids>
                        <parts>[[['q'], ['W+']], [['q'], ['W+']]]</parts>
                        <masses>[[9.92E+02 [GeV], 2.69E+02 [GeV], 1.29E+02 [GeV]], [9.94E+02 [GeV], 2.69E+02 [GeV], 1.29E+02 [GeV]]]</masses>
                        <ELweightPB>0.00250422094639</ELweightPB>
                    </elem>
                    <elem>
                        <pids>[[[1000001, 1000024, 1000022], [1000001, 1000024, 1000022]]]</pids>
                        <parts>[[['q'], ['W+']], [['q'], ['W-']]]</parts>
                        <masses>[[9.94E+02 [GeV], 2.69E+02 [GeV], 1.29E+02 [GeV]], [9.94E+02 [GeV], 2.69E+02 [GeV], 1.29E+02 [GeV]]]</masses>
                        <ELweightPB>0.000446091603342</ELweightPB>
                    </elem>
                    <elem>
                        <pids>[[[1000002, 1000024, 1000022], [1000002, 1000024, 1000022]], [[1000002, 1000024, 1000022], [1000004, 1000024, 1000022]], [[1000002, 1000024, 1000022], [1000004, 1000024, 1000022]], [[1000002, 1000024, 1000022], [1000002, 1000024, 1000022]], [[1000002, 1000024, 1000022], [1000004, 1000024, 1000022]], [[1000002, 1000024, 1000022], [1000004, 1000024, 1000022]], [[1000004, 1000024, 1000022], [1000002, 1000024, 1000022]], [[1000004, 1000024, 1000022], [1000004, 1000024, 1000022]], [[1000004, 1000024, 1000022], [1000004, 1000024, 1000022]]]</pids>
                        <parts>[[['q'], ['W+']], [['q'], ['W-']]]</parts>
                        <masses>[[9.92E+02 [GeV], 2.69E+02 [GeV], 1.29E+02 [GeV]], [9.92E+02 [GeV], 2.69E+02 [GeV], 1.29E+02 [GeV]]]</masses>
                        <ELweightPB>0.000244438105114</ELweightPB>
                    </elem>
                    <elem>
                        <pids>[[[1000004, 1000024, 1000022], [1000001, 1000024, 1000022]], [[1000004, 1000024, 1000022], [1000001, 1000024, 1000022]], [[1000002, 1000024, 1000022], [1000001, 1000024, 1000022]], [[1000002, 1000024, 1000022], [1000001, 1000024, 1000022]]]</pids>
                        <parts>[[['q'], ['W-']], [['q'], ['W-']]]</parts>
                        <masses>[[9.92E+02 [GeV], 2.69E+02 [GeV], 1.29E+02 [GeV]], [9.94E+02 [GeV], 2.69E+02 [GeV], 1.29E+02 [GeV]]]</masses>
                        <ELweightPB>7.13347138085e-05</ELweightPB>
                    </elem>
                </elem_list>
            </topology>

    """


if __name__ == "__main__":
    import doctest
    doctest.testmod()
