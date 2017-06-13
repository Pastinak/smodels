#!/usr/bin/env python3

"""
.. module: missingSimplifiedModels
   :synopsis: From missing PIDs and missing topologies
              build a missing simplified modellist.

.. moduleauthor:: Jory Sonneveld <jory@opmijnfiets.nl>

"""

from smodels.tools import tdict
from physicsUnits import GeV, pb
from math import floor, log10
from smodels.tools import txNames
from smodels.tools import txDecays
from smodels.theory import element
from smodels import particles
from smodels.tools import txNames


def getElementList(missing_topos):
    """
    Given the missing Topologies of an slha file, aggregate all contributing elements into a list
    """
    el_list = []
    for topo in missing_topos:
        for el in topo.contributingElements:
            el_list.append(el)
    return el_list
def findTxName(elem):
    """
    Given an element, find its TxName. The tdict needs the finalstate and the intermediates to determine the txname without ambiguity.
    """
    finalstate = str(elem.getParticles()).replace(' ', '').replace('+','').replace('-','').replace('jet','q')#.replace("'mu','nu'","'L','nu'").replace("'e','nu'","'L','nu'").replace("'ta','nu'","'L','nu'")
    #finalstate format is [[Branch1_smparticles],[Branch2_smparticles]]
    #intermediates format is [[Branch1_intermediates],[Branch2_intermediates]]
    prod_pid_b1 = elem.branches[0].PIDs[0]
    sptcs_b1 = []
    sptcs_b2 = [] 
    prod_pid_b2 = elem.branches[1].PIDs[0]
    #use particles.py to convert pids to strings, as squark pids are not unique
    for pid in prod_pid_b1:
        pid = particles.rOdd[abs(int(pid))].replace('C1', 'C').replace('C2', 'C').replace('N1', 'N').replace('N2', 'N').replace('N3', 'N').replace('N4', 'N')
        sptcs_b1.append(pid)
#        pid = pid.replace('C1', 'C').replace('C2', 'C').replace('N1', 'N').replace('N2', 'N').replace('N3', 'N').replace('N4', 'N')
        # change neutralino/chargino designation to not distinguish between the different charginos/neutralinos, e.g. C1 to C
    for pid in prod_pid_b2:
        pid = particles.rOdd[abs(int(pid))].replace('C1', 'C').replace('C2', 'C').replace('N1', 'N').replace('N2', 'N').replace('N3', 'N').replace('N4', 'N')
        sptcs_b2.append(pid) 
        # change neutralino/chargino designation to not distinguish between the different charginos/neutralinos, e.g. C1 to C
    intermediates = [sptcs_b1,sptcs_b2]
    
    branch1 = elem.branches[0]
    branch2 = elem.branches[1]
    if elem.motherElements:
        branch1 = elem.motherElements[0][1].branches[0]
        branch2 = elem.motherElements[0][1].branches[1]
#    print branch1, branch2
    contains_offshell = True
    while contains_offshell: #while iteration to get rid of all off shell decays, not just the first one that is found
        contains_offshell = False
        if elem.motherElements:
            os_decayinfo = find_offshell_decay(branch1,branch2,elem.motherElements[0][1])#need uncompressed element to determine offshell decays
        else:
            os_decayinfo = find_offshell_decay(branch1,branch2,elem)
#        if elem.elID == 24:
#            print os_decayinfo[0]
        if os_decayinfo[0]:#check whether the mass difference of possible off decays allow for off-shell decay
            finalstate = fs_offdecay(finalstate,os_decayinfo[1],os_decayinfo[2],os_decayinfo[3],os_decayinfo[4]) #change off-shell decay products to off-shell particle. this only checks for one type of off-shell processes.
            branch1 = finalstate[0] #change to off-shell version of branch in order to feed into check_offshell_decay again (to find possible occurence of different offshell decay than the one found already)
            branch2 = finalstate[1]
            contains_offshell = True
    inv_finalstate = [branch2,branch1]
    inv_intermediates = [sptcs_b2,sptcs_b1]
    targument = str((finalstate,intermediates)).replace(' ','').replace('"','').replace("'","")
    inv_targument = str((inv_finalstate,inv_intermediates)).replace(' ','').replace('"','').replace("'","")
    if targument in tdict.txnames: #need to either fix the order of particles or check every permutation
        #print 'found txname!'
        return tdict.txnames[targument]
    elif inv_targument in tdict.txnames:
        return tdict.txnames[inv_targument]
    else:
        #print targument
        return 'None'
def find_offshell_decay(branch1,branch2,elem):
    """
    Given the branches of an Element, finds off-shell decays in the finalstate.
    only considers the top, W and Z offshell decays.
    returns a boolean, the name of the sm particle that decayed off-shell, the branch and vertex in which it happened, the decaymode of the off-shell decay [bool,particle,branch,vertex,decaymode] e.g. [True, Woff, 2, 2, q,q]
    FIXME: function possibly not smart enough to distinguish between weak production of q,qbar finalstate and strong production of the same
    FIXME: no direct check if decay via sm particle is allowed for the sparticles involved in case of top quark
    """
    #List of decaymodes of W,Z,t
    #Woff = ["q,q","q,b","b,q","b,c","c,b","c,q","q,c","L,nu","nu,L","l,nu","nu,l","e,nu","nu,e","mu,nu","nu,mu","ta,nu","nu,ta"] #contains all decays of the W boson
    #Zoff = ["q,q","c,c","b,b","e,e","mu,mu","ta,ta"]
    #toff = ["W,b","b,W"]
    Woff = ["q,q","q,b","b,q","b,c","c,b","c,q","q,c","L,nu","nu,L","l,nu","nu,l","e,nu","nu,e","mu,nu","nu,mu","ta,nu","nu,ta","'q','q'","'q','b'","'b','q'","'b','c'","'c','b'","'c','q'","'q','c'","'L','nu'","'nu','L'","'l','nu'","'nu','l'","'e','nu'","'nu','e'","'mu','nu'","'nu','mu'","'ta','nu'","'nu','ta'"] #contains all (visible) decays of the W,Z,t. everything is in duplicate with different formats
    Zoff = ["q,q","c,c","b,b","e,e","mu,mu","ta,ta","'q','q'","'c','c'","'b','b'","'e','e'","'mu','mu'","'ta','ta'"]
    toff = ["W,b","b,W","'W','b'","'b','W'"]
    decayswithW = [['squark','squark'],['C','N'],['N','C'],['slepton','sneutrino'],['sneutrino','slepton']]
    decayswithZ = [['squark','squark'],['slepton','slepton'],['sneutrino','sneutrino'],['C','C'],['N','N']]
    masses = [elem.branches[0].masses,elem.branches[1].masses]#masses of the Rodd particles
    if type(branch1) != str and type(branch2) != str:
        ptcsb1 = str(branch1.particles).replace(' ', '').replace('+','').replace('-','').replace('jet','q').replace("'","")
        ptcsb2 = str(branch2.particles).replace(' ', '').replace('+','').replace('-','').replace('jet','q').replace("'","")
    else:
        ptcsb1 = branch1
        ptcsb2 = branch2
    for decaymode in Woff:
        if decaymode in ptcsb1:
            vertexnr = -1#branches always open 2 brackets before first particle, if decaymode is in 1st vertex, vertexnr will be 1
            #need to find vertex where 'decaymode' was found in order to compute correct mass difference. 
            for char in ptcsb1[:ptcsb1.find(decaymode)]:# loops over every char in finalstate until it hits 'decaymode'
                if char == '[':
                    vertexnr +=1
            sptc1_pid = int(elem.branches[0].PIDs[0][vertexnr-1])#sparticles pid
            sptc2_pid = int(elem.branches[0].PIDs[0][vertexnr])
            sptc1_name = particles.rOdd[sptc1_pid].replace('C1', 'C').replace('C2', 'C').replace('N1', 'N').replace('N2', 'N').replace('N3', 'N').replace('N4', 'N')#sparticle name, e.g. gluino
            sptc2_name = particles.rOdd[sptc2_pid].replace('C1', 'C').replace('C2', 'C').replace('N1', 'N').replace('N2', 'N').replace('N3', 'N').replace('N4', 'N')
            if vertexnr >= 1 and abs(masses[0][vertexnr-1] - masses[0][vertexnr]).asNumber(GeV) < 80.4:#check if mass difference allows W. FIXME: does not yet include the other sm particles in vertex!
                if abs(particles.qNumbers[abs(sptc1_pid)][1] - particles.qNumbers[abs(sptc2_pid)][1]) == 3:#Check whether the sparticle charges are correct for W decay
                    if [sptc1_name,sptc2_name] in decayswithW:#check if W is allowed at the vertex
                        return [True,'Woff',1,vertexnr,decaymode]
        if decaymode in ptcsb2:
            vertexnr = -1#branches always open 2 brackets before first particle, if decaymode is in 1st vertex, vertexnr will be 1
            #need to find vertex where 'decaymode' was found in order to compute correct mass difference. 
            for char in ptcsb2[:ptcsb2.find(decaymode)]:# loops over every char in finalstate until it hits 'decaymode'
                if char == '[':
                    vertexnr +=1
            sptc1_pid = int(elem.branches[1].PIDs[0][vertexnr-1])
            sptc2_pid = int(elem.branches[1].PIDs[0][vertexnr])
            sptc1_name = particles.rOdd[sptc1_pid].replace('C1', 'C').replace('C2', 'C').replace('N1', 'N').replace('N2', 'N').replace('N3', 'N').replace('N4', 'N')#sparticle name, e.g. gluino
            sptc2_name = particles.rOdd[sptc2_pid].replace('C1', 'C').replace('C2', 'C').replace('N1', 'N').replace('N2', 'N').replace('N3', 'N').replace('N4', 'N')
            if vertexnr >= 1 and abs(masses[1][vertexnr-1] - masses[1][vertexnr]).asNumber(GeV) < 80.4:#check if mass difference allows W. FIXME: does not yet include the other sm particles in vertex!
                if abs(particles.qNumbers[abs(sptc1_pid)][1] - particles.qNumbers[abs(sptc2_pid)][1]) == 3:
                    if [sptc1_name,sptc2_name] in decayswithW:#check if W is allowed at the vertex
                        return [True,'Woff',2,vertexnr,decaymode]
    for decaymode in Zoff:
        if decaymode in ptcsb1:
            vertexnr = -1#branches always open 2 brackets before first particle, if decaymode is in 1st vertex, vertexnr will be 1
            #need to find vertex where 'decaymode' was found in order to compute correct mass difference. 
            for char in ptcsb1[:ptcsb1.find(decaymode)]:# loops over every char in finalstate until it hits 'decaymode'
                if char == '[':
                    vertexnr +=1
            sptc1_pid = int(elem.branches[0].PIDs[0][vertexnr-1])
            sptc2_pid = int(elem.branches[0].PIDs[0][vertexnr])
            sptc1_name = particles.rOdd[sptc1_pid].replace('C1', 'C').replace('C2', 'C').replace('N1', 'N').replace('N2', 'N').replace('N3', 'N').replace('N4', 'N')#sparticle name, e.g. gluino
            sptc2_name = particles.rOdd[sptc2_pid].replace('C1', 'C').replace('C2', 'C').replace('N1', 'N').replace('N2', 'N').replace('N3', 'N').replace('N4', 'N')
            if vertexnr >= 1 and abs(masses[0][vertexnr-1] - masses[0][vertexnr]).asNumber(GeV) < 91.1:#check if mass difference allows Z. FIXME: does not yet include the other sm particles in vertex!
                if particles.qNumbers[abs(sptc1_pid)][1] == particles.qNumbers[abs(sptc2_pid)][1]:
                    if [sptc1_name,sptc2_name] in decayswithZ:#check if Z is allowed at the vertex
                        return [True,'Zoff',1,vertexnr,decaymode]
        if decaymode in ptcsb2:
            vertexnr = -1#branches always open 2 brackets before first particle, if decaymode is in 1st vertex, vertexnr will be 1
            #need to find vertex where 'decaymode' was found in order to compute correct mass difference. 
            for char in ptcsb2[:ptcsb2.find(decaymode)]:# loops over every char in finalstate until it hits 'decaymode'
                if char == '[':
                    vertexnr +=1
            sptc1_pid = int(elem.branches[1].PIDs[0][vertexnr-1])
            sptc2_pid = int(elem.branches[1].PIDs[0][vertexnr])
            sptc1_name = particles.rOdd[sptc1_pid].replace('C1', 'C').replace('C2', 'C').replace('N1', 'N').replace('N2', 'N').replace('N3', 'N').replace('N4', 'N')#sparticle name, e.g. gluino
            sptc2_name = particles.rOdd[sptc2_pid].replace('C1', 'C').replace('C2', 'C').replace('N1', 'N').replace('N2', 'N').replace('N3', 'N').replace('N4', 'N')
            if vertexnr >= 1 and abs(masses[1][vertexnr-1] - masses[1][vertexnr]).asNumber(GeV) < 81.1:#check if mass difference allows Z. FIXME: does not yet include the other sm particles in vertex!
                if particles.qNumbers[abs(sptc1_pid)][1] == particles.qNumbers[abs(sptc2_pid)][1]:
                    if [sptc1_name,sptc2_name] in decayswithZ:#check if Z is allowed at the vertex
                        return [True,'Zoff',2,vertexnr,decaymode]
    for decaymode in toff:
        if decaymode in ptcsb1:
            vertexnr = -1#branches always open 2 brackets before first particle, if decaymode is in 1st vertex, vertexnr will be 1
            #need to find vertex where 'decaymode' was found in order to compute correct mass difference. 
            for char in ptcsb1[:ptcsb1.find(decaymode)]:# loops over every char in finalstate until it hits 'decaymode'
                if char == '[':
                    vertexnr +=1
            sptc1_pid = int(elem.branches[0].PIDs[0][vertexnr-1])
            sptc2_pid = int(elem.branches[0].PIDs[0][vertexnr])
            if vertexnr >= 1 and abs(masses[0][vertexnr-1] - masses[0][vertexnr]).asNumber(GeV) < 173.:#check if mass difference allows t. FIXME: does not yet include the other sm particles in vertex!
                if abs(particles.qNumbers[abs(sptc1_pid)][1] - particles.qNumbers[abs(sptc2_pid)][1]) == 2: #FIXME: this will not recognize decays where another sm particle with charge !=0 is in the vertex!
                    return [True,'toff',1,vertexnr,decaymode]
        if decaymode in ptcsb2:
            vertexnr = -1#branches always open 2 brackets before first particle, if decaymode is in 1st vertex, vertexnr will be 1
            #need to find vertex where 'decaymode' was found in order to compute correct mass difference. 
            for char in ptcsb2[:ptcsb2.find(decaymode)]:# loops over every char in finalstate until it hits 'decaymode'
                if char == '[':
                    vertexnr +=1
            sptc1_pid = int(elem.branches[1].PIDs[0][vertexnr-1])
            sptc2_pid = int(elem.branches[1].PIDs[0][vertexnr])
            if vertexnr >= 1 and abs(masses[1][vertexnr-1] - masses[1][vertexnr]).asNumber(GeV) < 173.:#check if mass difference allows t. FIXME: does not yet include the other sm particles in vertex!
                if abs(particles.qNumbers[abs(sptc1_pid)][1] - particles.qNumbers[abs(sptc2_pid)][1]) == 2: #FIXME: this will not recognize decays where another sm particle with charge !=0 is in the vertex!
                    return [True,'toff',2,vertexnr,decaymode]
    return [False,'None',-1,-1,'None']
def fs_offdecay(finalstate,os_ptc,branchnr,vertexnr,decaymode):
    """
    Changes the finalstate to have the off-shell decay where indicated
    param finalstate: finalstate with offshell candidate as string
    param os_ptc: sm particle that decayed off-shell, e.g. 'Woff'
    param branchnr: integer indicates which branch the off-shell decay was found. either 1 or 2
    param vertexnr: indicates the vertex where the off-shell decay occured
    param decaymode: the string of the decaymode that is to be replaced by os_ptc, e.g. 'q,q'

    FIXME: possible problem: one occurence of the decaymode was cause by offshell decay, another was not (e.g. Woff->jet jet, where jet jet can be caused by a lot of processes.)
    """
    fs = str(finalstate).replace(' ', '').replace('+','').replace('-','').replace('jet','q').replace("'","")#.replace("'","")
    index = 1
    vertex = 0
    if fs[:3].count('[') == 2:#case of empty first branch, normal finalstate should have 3 times [
        branch1 = fs[1:3]
        branch2 = fs[4:-1]
    else:
        #print fs
        for char in fs[2:]:#this idenfies the branches
            index+=1
            if char == '[':
                vertex+=1
            if char == ']':
                vertex-=1
                if vertex == -1:#index is now at the position of the last bracket in the first branch
                    branch1 = fs[1:index+1]
                    branch2 = fs[index+2:-1]
                    break
    if branchnr == 1:
        branchvertex = -1
        charindex = -1
        vertexlen = 0
        for char in branch1:
            charindex+=1
            if char == '[':
                branchvertex+=1
                if branchvertex == vertexnr:#charindex is now marks the beginning of the vertex where the decaymode was found
                    vertexlen = branch1[charindex:].find(']')#need this to limit replace function
                    break
        branch1 = branch1[:charindex] + branch1[charindex:charindex+vertexlen].replace(decaymode,os_ptc)+branch1[charindex+vertexlen:]
    if branchnr == 2:
        branchvertex = -1
        charindex = -1
        vertexlen = 0
        for char in branch2:
            charindex+=1
            if char == '[':
                branchvertex+=1
                if branchvertex == vertexnr:#charindex is now marks the beginning of the vertex where the decaymode was found
                    vertexlen = branch2[charindex:].find(']')#need this to limit replace function
                    break
        branch2 = branch2[:charindex] + branch2[charindex:charindex+vertexlen].replace(decaymode,os_ptc)+branch2[charindex+vertexlen:]                
                
    fs_corr = [branch1,branch2] #possible problem: format is different than in tdict. ['[[b,t],[Z],[Woff]]', '[[b,t],[Z],[Woff]]'] is an example
    return fs_corr

def getTxNames(el_list,mistop_sqrts):
    """
    Given an element list, find all txnames and sort them by their weight.
    Returns a dictionary with TxNames and their Weight, a list of the txNames that is sorted according to the weights and a dictionary with txnames and contributing elements
    """
    
    txWeights = {}#dictionary containing txname as key and the weight as value {'txname': weight[pb]}
    txElements = {}#dictionary containing all contributing elements to a txname {'txname': [contributing elements]}
    for el in el_list:
        txName = findTxName(el)
        #if txname already in txList, add element weight to its corresponding topology weight
        if txName in txWeights:
            txWeights[txName] += el.weight.getXsecsFor(mistop_sqrts)[0].value.asNumber(pb)
            txElements[txName].append(el)
        #else create an entry in txElements and in txWeights
        else:
            txWeights[txName] = el.weight.getXsecsFor(mistop_sqrts)[0].value.asNumber(pb)
            txElements[txName] = [el]
            #convert weights to pb
#    print txWeights
    """for weight in txWeights.values():
        if type(weight)
        print weight
        weight = weight.asNumber(pb)
        print weight"""
    #sort txWeights
    txSorted = sorted(txWeights, key=txWeights.__getitem__, reverse=True)
    return txWeights, txSorted, txElements
    

    
def mlsp(elem):
    """
    Given an Element, return the lightest particle mass.

    >>> from smodels.theory import slhaDecomposer
    >>> smstoplist = slhaDecomposer.decompose('inputFiles/slha/complicated.slha')
    >>> elements = smstoplist.getElements()
    >>> el1 = elements[1]
    >>> el1.getMasses()
    [[1.29E+02 [GeV]], [2.69E+02 [GeV], 1.29E+02 [GeV]]]
    >>> min(el1.getMasses())
    [1.29E+02 [GeV]]
    >>> a = []
    >>> a.extend([mass for mass in masses for masses in el1.getMasses()])
    >>> a
    [2.69E+02 [GeV], 2.69E+02 [GeV], 1.29E+02 [GeV], 1.29E+02 [GeV]]
    >>> a = []
    >>> a.extend([mass for mass in masses for el in elements for masses in el.getMasses()])
    >>> list(set(a))
    [1.29E+02 [GeV], 8.65E+02 [GeV], 2.69E+02 [GeV], 9.91E+02 [GeV]]
    >>> min(list(set(a)))
    1.29E+02 [GeV]

    """
    # Note: instead of going through entire smstoplist, one take the last partice in decay chains
    # which should always be an lsp
    # To check if it is really the LSP and not a compressed particle on can get the mother
    # and whether the particle was actually compressed. Need to check this still.
    massesGeV = []
    masses = elem.getMasses()
    #check if the element was compressed
    if not elem.motherElements:
        massesGeV.extend([mass for mass in masses])
    #if it was compressed, use the uncompressed element instead
    else:
        for mom in elem.motherElements:
            #if mom[1].elID == elem.elID: this was in Andre's code for solving double counting. Not sure what it does/if it's needed
                masses = mom[1].getMasses()
                massesGeV.extend([mass for mass in masses])

    if not massesGeV:
        return None
    else:
        #return the lightest  SUSY particle in the cascade. Should always be the LSP
        #careful! massesGeV is a list of lists, return min(massesGeV) returns a branch
        return min(min(massesGeV))

def round_to_sign(x, sig=3):#currently not used
    """
    Round the given number to the significant number of digits.
    """
    rounding = sig - int(floor(log10(x))) - 1
    if rounding == 0:
        return int(x)
    else:
        return round(x, rounding)

def sms_name(elem):#Currently not used
    """
    Return sms name from tdict given the element from which a final state can be extracted.
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

    #tx = txNames.getTx(elem)
    finalstate = elem.getParticles()
#    print(finalstate)
    #print(tx, pids, parts)
    #decays = txDecays.decays
    #txes = {'T2': 'signature': "[[[jet]],[[jet]]]", 'particles': "[[[1000002, 1000022], [1000021, 1000022]]]"}
    #{'T2': 'signature': "[[[jet]],[[jet]]]", 'particles': "[[[1000002, 1000022], [1000021, 1000022]]]"}

    #remove charges and rename/group various particles to match tdict. In case of Woff decay into leptons, all leptons are possible decaymodes, thus change to L
    fs = str(finalstate).replace(' ', '').replace('+','').replace('-','').replace('q','jet').replace("'mu','nu'","'L','nu'").replace("'e','nu'","'L','nu'").replace("'ta','nu'","'L','nu'")
#    print fs
    if fs in tdict.tdict:
        if check_production(elem,tdict.tdict[fs]):
            return tdict.tdict[fs]
        
        elif tdict.tdict[fs] in tdict.double_names and check_production(elem,tdict.double_names[tdict.tdict[fs]]):#checks whether the branch progenitors fit the alternative txname.
            return tdict.double_names[tdict.tdict[fs]] #does this implementation work with chains of double names?
        else:
            return None
    else:
        for finalstatestring in tdict.tdict:
            el = element.Element(finalstatestring)
            # Need literal eval or not? See examples above.
            if el.particlesMatch(elem):
                if check_production(elem,tdict.tdict[finalstatestring]):
                    return tdict.tdict[finalstatestring]
                elif tdict.tdict[finalstatestring] in tdict.double_names and check_production(elem,tdict.double_names[tdict.tdict[finalstatestring]]):#checks whether the branch progenitors fit the alternative txname. 
                    return tdict.double_names[tdict.tdict[finalstatestring]] #does this implementation work with chains of double names?      
                else:
                    return None
        return None
def check_production(elem,txname):#Currently not used
    """
    -- given an element and a txname, checks whether the production mechanism of the element matches the txname production mechanism
    #create a dictionary that links txname to production mechanism.
    # currently made additional dictionary manually in tdict. need to change maketdict to include new dictionary, otherwise it gets lost when maketdict is executed
    # double names not included
    """
    prod_pid_b1 = abs(elem.branches[0].PIDs[0][0])
    prod_pid_b2 = abs(elem.branches[1].PIDs[0][0])
#    print(prod_pid_b1)
#    print(prod_pid_b2)
    #use particles.py to convert pids to strings, as squark pids are not unique
    prod_pid_b1 = particles.rOdd[int(prod_pid_b1)]
#    print(prod_pid_b1)
    prod_pid_b2 = particles.rOdd[int(prod_pid_b2)]
#    print(prod_pid_b2)
    # change neutralino/chargino designation to not distinguish between the different charginos/neutralinos, e.g. C1 to C
    prod_pid_b1 = prod_pid_b1.replace('C1', 'C').replace('C2', 'C').replace('N1', 'N').replace('N2', 'N').replace('N3', 'N').replace('N4', 'N')
#    print(prod_pid_b1)
    prod_pid_b2 = prod_pid_b2.replace('C1', 'C').replace('C2', 'C').replace('N1', 'N').replace('N2', 'N').replace('N3', 'N').replace('N4', 'N')
#    print(prod_pid_b2)
    txprefix = "NoneFound"
    # format of prod_pids should be: key: [branch 1 progenitor, branch 2 progenitor]
    # prod pids only contains prefix, e.g. T1 ,T2 etc. Need to only consider prefix in txname
#    print txname
    if txname.find("TChi") != -1: #this means it found 'TChi'
        if txname.find("TChiChipm") == -1 and txname.find("TChipChim") == -1: #TChiChipm and TChipChim dont occur
            txprefix = "TChi" #assigns the value 
            #print txprefix
        elif txname.find("TChiChipm") != -1:
            txprefix = "TChiChipm"
        elif txname.find("TChipChim") != -1:
            txprefix = "TChipChim"
    elif txname.find("T1") != -1:
        txprefix = "T1"
        #print txprefix
    elif txname.find("T2") != -1:
        txprefix = "T2"
        #print txprefix
    elif txname.find("T3") != -1:
        txprefix = "T3"
        #print txprefix
    elif txname.find("T4") != -1:
        txprefix = "T4"
        #print txprefix
    elif txname.find("T5") != -1:
        txprefix = "T5"
        #print txprefix
    elif txname.find("T6") != -1:
        txprefix = "T6"
        #print txprefix
    if txprefix in tdict.prod_pids:
        if [prod_pid_b1,prod_pid_b2] == tdict.prod_pids[txprefix] or [prod_pid_b2,prod_pid_b1] == tdict.prod_pids[txprefix]: #Compares both orders the branch progenitors of the element against the ones required by the txname
            return True
    else:
        return False


def missing_elem_list(missing_elements, mistop_sqrts): #Currently not used
    """
    Given a bunch of elements, aggregate them into a list
    (ordered by weight) ignoring antiparticles and order,
    and group for like masses.
    """
    missing_elts = []
    elementdict = {}
    for elem in missing_elements:#[:10]:
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
        # Get nr of intermediate particles/branch length
        brlen = {'Branch 1': elem.branches[0].getLength(), 'Branch 2': elem.branches[1].getLength() }
        # Check whether the element was compressed
        hasmom = False
      #  print elem.motherElements
        if elem.motherElements:
            hasmom = True

        tx = sms_name(elem)
        # Get the neutralino mass
        lspmass = mlsp(elem)
        # Add weight if it only concerns antiparticles:
        if pids_no_minus in elementdict:
            elementdict[pids_no_minus]['ELweightPB'] += wt.asNumber(pb)
        # Add new element otherwise:
        else:
            elt = {'pids': str(pids_no_minus),
                    'ELweightPB': wt.asNumber(pb),
                    'Branch': branches, 'Txname': tx, 'isCompressed': hasmom, 'm_neutralino': lspmass.asNumber(GeV),
                   'N_intPtcs': brlen}
            elementdict[pids_no_minus] = elt
    for elt in sorted(elementdict.values(), key=lambda x: x['ELweightPB'], reverse=True):
        missing_elts.append(elt)
    return missing_elts


def missing_sms_dict(missing_topos, sqrts, nprint=10):#Currently not used
    """(MissingTopos)-> [list]

    Given a missing topology, which can be quite general
    in the sense that it only gives a certain final state,
    return the specific particle IDs and weights of what can
    be called missing simplified models.

    >>> 
    """
    mistop_sqrts = sqrts
    missing_topo_dict = {'topology': []}
    #doesn't work for asymmetric and long cascades, as the elements are saved in 'classes', not 'topos'
    for mistop in sorted(missing_topos.topos, key=lambda x: x.value, reverse=True)[:nprint]:
        topname = mistop.topo

        topweight = 0
        for el in mistop.contributingElements:
            if not el.weight.getXsecsFor(mistop_sqrts): continue
            topweight += el.weight.getXsecsFor(mistop_sqrts)[0].value.asNumber(pb)
        missing = {'topology': topname, 'TOPweightPB': topweight, 'sqrts': str(mistop_sqrts)}
        missing['elem'] = missing_elem_list(mistop.contributingElements, mistop_sqrts)
        missing_topo_dict['topology'].append(missing)
    missing_topo_dict['topology'].sort(key=lambda x: x['TOPweightPB'], reverse=True)
    return missing_topo_dict


def unique_particles(pids, final_states, masses):#Currently not used
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
