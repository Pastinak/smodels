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
    >>> tdict, double_names = make_tdict()
    >>> tdict[str(topo).replace(" ", "")]
    'T2bbWW'
    """
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

        for finalstate in finalstates:
            el = element.Element(ast.literal_eval(finalstate))
            #print el.getParticles()
            #print finalstate
            #print el.sortBranches()
            #print el.getParticles()
            finalstate_sorted = str(el.getParticles())

            if finalstate_sorted in d and d[finalstate_sorted] != tx:
                if d[finalstate_sorted] not in double_names:
                    double_names[d[finalstate_sorted]] = tx
                elif tx not in double_names:
                    double_names[tx] = d[finalstate_sorted]
                else:
                    print 'not adding double name', d[finalstate_sorted], tx
            # d[finalstate_sorted] = tx #not working
            d[finalstate] = tx
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
    #for k in d:
    #    if 'W' in k and 'b' in k:
    #        print k, d[k]
    tdictwrite = open("smodels/tools/tdict.py", "w")
    tdictwrite.write("tdict = " + str(d) + '\n\n')
    tdictwrite.write("double_names = " + str(double_names) + '\n')
    tdictwrite.close()



