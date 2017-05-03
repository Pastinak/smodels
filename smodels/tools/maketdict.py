#!/usr/bin/env python

from smodels.theory import element
from smodels.theory import particleNames
import ast
import os

def make_tdict(smodels_database_path='smodels-database', regenerate_constraints=True, filename="constraints"):
    """
    Make a tdictionary with finalstates as strings as keys
    and txnames as values.
    Return tdict and also a dictionary of double names where more than
    one txname fits a final state.

    Todo: generate tmpfile with constraints instead of giving filename.

    >>> topo = [[['b','W']],[['b','W']]]
    >>> el = element.Element(str(topo))
    >>> el.sortBranches()
    >>> topo = el.getParticles()
    >>> tdict, double_names = make_tdict()
    >>> tdict[str(topo).replace(" ", "")]
    'T2bbWW'


    >>> el = element.Element("[[['t'],['W']],[['t'],['W']]]")
    >>> print el
    [[[t],[W]],[[t],[W]]]
    >>> el2 = element.Element("[[['t'],['W']],[['W'],['t']]]")
    >>> print el2
    [[[t],[W]],[[W],[t]]]
    >>> el.particlesMatch(el)
    True
    >>> el2.sortBranches()
    >>> print el2
    [[[W],[t]],[[t],[W]]]

    """
    # Generate a file with all constraints that are to be included in the dictionary:
    if regenerate_constraints:
        if smodels_database_path.endswith('/'):
            smodels_database_path = smodels_database_path[:-1]
        os.system("grep constraint " + smodels_database_path + "/*/*/*/*data*/*.txt > " + filename)

    d = {}

    # Start reading file with constraints:
    f = open(filename, 'r')
    line = f.readline()
    double_names = {}
    while line != '':

        # txname, like T1bbbb:
        tx = line.split(':')[0].split('/')[-1][:-4]

        # There may be more than one final state written on one line separated by +
        finalstates = line.split(':')[-1][:-1].split(' + ')

        # Using smodels for parsing string:
        finalstates = particleNames.elementsInStr(finalstates, removeQuotes=False)

        for finalstate in finalstates:

            # Use smodels to create an element from the final state:
            el = element.Element(finalstate)

            # Sort the branches for faster lookup later:
            el.sortBranches()

            # Get the particles back (now in sorted format):
            finalstate_sorted = str(el.getParticles())

            # Forget about the charge:
            finalstate_chargeblind = finalstate_sorted.replace('-', '').replace('+', '')

            # Remove spaces:
            finalstate_chargeblind = finalstate_chargeblind.replace(' ', '')


            # If already in dictionary, keep track of double names:
            if finalstate_chargeblind in d and d[finalstate_chargeblind] != tx:
                if d[finalstate_chargeblind] not in double_names:
                    double_names[d[finalstate_chargeblind]] = tx
                elif tx not in double_names:
                    double_names[tx] = d[finalstate_chargeblind]
                else:
                    print 'not adding double name', d[finalstate_chargeblind], tx

            # Add to dictionary (overwrites in case of double name):
            d[finalstate_chargeblind] = tx

        # Go to next result in database:
        line = f.readline()

    return d, double_names


def more_txnames():
    """
    placeholder for more txnames that are not included in database.
    """
    d = {}
    # d['myfinalstate'] = 'Tmymodel'
    return d

if __name__ == "__main__":
    import doctest
    doctest.testmod()
    d, double_names = make_tdict()
    d.update(more_txnames())

    print d
    print double_names
    tdictwrite = open("smodels/tools/tdict.py", "w")
    tdictwrite.write("tdict = " + str(d) + '\n\n')
    tdictwrite.write("double_names = " + str(double_names) + '\n')
    tdictwrite.close()



