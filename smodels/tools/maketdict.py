#!/usr/bin/env python

from smodels.theory import element
from smodels.theory import particleNames
import ast

def make_tdict(smodels_database_path='smodels-database', regenerate_constraints=True, filename="constraints"):
    """
    Make a tdictionary with finalstates as strings as keys
    and txnames as values.
    Return tdict and also a dictionary of double names where more than
    one txname fits a final state.

    Todo: generate tmpfile with constraints instead of giving filename.

    >>> topo = [[['b','W']],[['b','W']]]
    >>> tdict, double_names = make_tdict()
    >>> tdict[str(topo).replace(" ", "")]
    'T2bbWW'
    """
    import os
    if regenerate_constraints:
        if smodels_database_path.endswith('/'):
            smodels_database_path = smodels_database_path[:-1]
        os.system("grep constraint " + smodels_database_path + "/*/*/*/data/*.txt > " + filename)

    print dir(particleNames)
    print help(particleNames.elementsInStr)
    d = {}
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

        print 'smodels finalstates:', finalstates
        for finalstate in finalstates:
            # Some final states in the database are combinations of final states
            # For building a dictionary, make multiple entries, one for each final state
            # a ]+] points at a combination, e.g.:
            # 2.*([[['L'],['L']],[['L'],['nu']]] + [[['L'],['L']],[['nu'],['L']]])
            if ']+[' in finalstate:
                # Remove brackets and so on from finalstate (see example above)
                if '(' in finalstate:
                    finalstate_nicelywritten = finalstate[finalstate.index('(') + 1:]
                finalstate_nicelywritten = finalstate_nicelywritten.strip(')')
                finalstates_no_combinations = finalstate_nicelywritten.split(']+[')
                finalstates_no_combinations = [finalstates_no_combinations[0] + ']'] + ['[' + di + ']' for di in finalstates_no_combinations[1:-1]] + ['[' + finalstates_no_combinations[-1]]
                finalstates.remove(finalstate)
                finalstates += finalstates_no_combinations
        for finalstate in finalstates:
            if '(' in finalstate:
                # This is still a composit finalstate and/or has a 2*( in front of it or so:
                finalstate_nicelywritten = finalstate[finalstate.index('(') + 1:]
            elif '*' in finalstate:
                # This is still a composit finalstate and/or has a 2*( in front of it or so:
                finalstate_nicelywritten = finalstate[finalstate.index('*') + 1:]
            else:
                finalstate_nicelywritten = finalstate
            finalstate_nicelywritten = finalstate_nicelywritten.strip(')').strip()
            finalstate_nicelywritten = finalstate_nicelywritten.replace('-', '').replace('+', '')

            # I still have this problem:
            # [[['t','t']],[['t','t']]]]
            if finalstate_nicelywritten.startswith("[[['") and finalstate_nicelywritten.endswith("']]]]"):
                print "rewriting finalstate", finalstate_nicelywritten
                finalstate_nicelywritten = finalstate_nicelywritten[:-1]
            if finalstate_nicelywritten.startswith("[[[['") and finalstate_nicelywritten.endswith("']]]"):
                print "rewriting finalstate", finalstate_nicelywritten
                finalstate_nicelywritten = finalstate_nicelywritten[1:]

            # Todo: Read out from database as it is done before!

            # Now try to sort the finalstate:
            print finalstate_nicelywritten
            el = element.Element(ast.literal_eval(finalstate_nicelywritten))
            el.sortBranches()
            finalstate_sorted = str(el.getParticles())

            if finalstate_sorted in d and d[finalstate_sorted] != tx:
                if d[finalstate_sorted] not in double_names:
                    double_names[d[finalstate_sorted]] = tx
                elif tx not in double_names:
                    double_names[tx] = d[finalstate_sorted]
                else:
                    print 'not adding double name', d[finalstate_sorted], tx
            d[finalstate_sorted] = tx
        line = f.readline()

    return d, double_names


if __name__ == "__main__":
    import doctest
    doctest.testmod()
    #print "Please first create new constraints:"
    #print "grep constraint ../../smodels-database/*/*/*/data/*.txt > constraints"
    #print ''
    d, double_names = make_tdict()

    print d
    print double_names
    for k in d:
        if 'W' in k and 'b' in k:
            print k, d[k]
    tdictwrite = open("smodels/tools/tdict.py", "w")
    tdictwrite.write("tdict = " + str(d) + '\n\n')
    tdictwrite.write("double_names = " + str(double_names) + '\n')
    tdictwrite.close()



