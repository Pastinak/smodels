#!/usr/bin/env python2

def make_tdict(smodels_database_path='../../smodels-database', regenerate_constraints=True, filename="constraints"):
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

    d = {}
    f = open(filename, 'r')
    line = f.readline()
    double_names = {}
    while line != '':
        tx = line.split(':')[0].split('/')[-1][:-4]
        dinges = line.split(':')[-1][:-1].split(' + ')
        for ding in dinges:
            if ']+[' in ding:
                #print "ding", ding
                if '(' in ding:
                    din = ding[ding.index('(') + 1:]
                din = din.strip(')')
                nieuwedingen = din.split(']+[')
                nieuwedingen = [nieuwedingen[0] + ']'] + ['[' + di + ']' for di in nieuwedingen[1:-1]] + ['[' + nieuwedingen[-1]]
                dinges.remove(ding)
                dinges += nieuwedingen
        for ding in dinges:
            if '(' in ding:
                din = ding[ding.index('(') + 1:]
            elif '*' in ding:
                din = ding[ding.index('*') + 1:]
            else:
                din = ding
            din = din.strip(')').strip()
            if din in d and d[din] != tx:
                #print 'din already in dictionary! this one:', din
                #print 'topology name was: ', d[din], 'is:', tx
                if d[din] not in double_names:
                    double_names[d[din]] = tx
                elif tx not in double_names:
                    double_names[tx] = d[din]
                else:
                    print 'not adding double name', d[din], tx
            d[din] = tx
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
    tdictwrite = open("tdict.py", "w")
    tdictwrite.write("tdict = " + str(d) + '\n\n')
    tdictwrite.write("double_names = " + str(double_names) + '\n')
    tdictwrite.close()



