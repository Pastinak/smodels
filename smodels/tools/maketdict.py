from collections import OrderedDict
import os
#particle/sparticle dictionaries
q = {'q': 'squark', 'c': 'squark', 'b':'sbottom','t':'stop','toff':'stop'}
l = {'e': 'slepton', 'mu': 'slepton','ta':'stau','nu':'sneutrino'}
b = ['Z','Zoff','W','Woff']

#Chargino decay dictionary
Cdecays = {('q','squark'):'q',('q','squark'):'q',('q','sbottom'):'q',('q','stop'):'q',('c','squark'):'c',('c','sbottom'):'c',('c','stop'):'c',('b','stop'):'b',('t','sbottom'):'t',('toff','sbottom'):'toff',#quark vertices
           ('e','sneutrino'):'l',('mu','sneutrino'):'l',('ta','sneutrino'):'ta',#lepton vertices
           ('nu','slepton'):'nu',('nu','stau'):'nu', #neutrino vertices
           ('Z','C'):'Z',('Zoff','C'):'Zoff',#Z vertices
           ('photon','C'):'ga',#photon
           ('higgs','C'):'h',('H0','C'):'H',('A0','C'):'A',#via higgs
           ('H','N'):'Hpm', #via charged higgs
           ('W','N'):'W',('Woff','N'):'Woff',#W vertices
           ('q,q','gluino'):'qq', ('q,c','gluino'):'qc', ('q,b','gluino'):'qb',('c,b','gluino'):'cb',('t,b','gluino'):'tb',('t,q','gluino'):'tq',
}
#Neutralino decay dictionary
Ndecays = {('q','squark'):'q',('c','squark'):'c',('b','sbottom'):'b',('t','stop'):'t',('toff','stop'):'toff', #quark decays
           ('Z','N'):'Z',('nu,nu','N'):'Z',('','N'):'Z',('Zoff','N'):'Zoff',#Z decays
           ('photon','N'):'ga',#Via photon
           ('higgs','N'):'h',('H0','N'):'H',('A0','N'):'A',#via higgs
           ('W','C'):'W',('Woff','C'):'Woff',('H','C'):'Hpm', #t chargino
           ('q,q','gluino'):'qq',('c,c','gluino'):'cc',('b,b','gluino'):'bb',('t,t','gluino'):'tt',
}

#for now, only interested in decays to lsp for quarks -> trivial (q,N) and (c,N)
#'light' squark decay dictionary
Sqdecays = {('q','N'):'q',('c','N'):'c',
            ('q','C'):'q',('c','C'):'c',('b','C'):'b',('t','C'):'t',
            ('q','gluino'):'q'
}
#Scharm decay dictionary
#Scdecays = {('c','N'):'c',
#            ('g','gluino'):'g'
#} scharms not implemented in smodels
#Sbottom decay dictionary
Sbdecays = {('b','N'):'b',
            ('t','C'):'b',
            ('g','gluino'):'g'
}
#Stop decay dictionary
Stdecays = {('t','N'):'t',('toff','N'):'toff',
            ('b','C'):'b',
            ('g','gluino'):'g'
}

#Slepton decay dictionary
Sldecays = {('e','N'):'l',('mu','N'):'l',#to neutralino
            ('nu','C'):'nu'#to chargino
}
#Stau decay dictionary
Staudecays = {('ta','N'):'ta',#to neutralino
              ('nu','C'):'nu'#to chargino
}
#Sneutrino decay dictionary
Snudecays = {('nu','N'):'nu',('','N'):'nu',#to neutralino
             ('e','C'):'l',('mu','C'):'l',('ta','C'):'ta',#to chargino #use generic l for leptons or e&mu?
}
Gldecays = {('q,q','N'):'qq',('c,c','N'):'cc',('t,t','N'):'tt',('b,b','N'):'bb',
            ('q,q','C'):'qq', ('q,c','C'):'qc', ('q,b','C'):'qb',('c,b','C'):'cb',('t,b','C'):'tb',('t,q','C'):'tq',
            ('q','squark'):'q',('c','squark'):'c',('b','sbottom'):'b',('t','stop'):'t'
}
#dictionary assigning the decay dictionary to use to the sparticle in question
whatdecay = {'squark': Sqdecays,
             'sbottom': Sbdecays,
             'stop': Stdecays,
             'slepton':Sldecays,
             'stau': Staudecays,
             'sneutrino': Snudecays,
             'C': Cdecays,
             'N': Ndecays,
             'gluino': Gldecays
}
#dictionary to assign Tname prefix to a given productionmode
tname = {('N','N'): 'ChiChi',
         ('C','C'): 'ChipChim',
         ('C','N'): 'ChiChipm',
         ('N','C'): 'ChiChipm',
         ('slepton','slepton'): 'SlepSlep',
         ('sneutrino','sneutrino'): 'SnuSnu',
         ('slepton','sneutrino'): 'SlepSnu',
         ('sneutrino','slepton'): 'SlepSnu',

#         ('sneutrino','squark'): 'SnuSq',
#         ('sneutrino','sbottom'): 'SnuSb',
#         ('sneutrino','scharm'): 'SnuSc',
         ('stau','sneutrino'): 'StauSnu',
         ('sneutrino','stau'): 'StauSnu',

         ('gluino','gluino'): '1',
         
         ('squark','squark'): '2',
         ('sbottom','sbottom'): '2',
         ('stop','stop'): '2',

         ('squark','sbottom'): '2',
         ('squark','stop'): '2',
         ('sbottom','squark'): '2',
         ('stop','squark'): '2',
         ('sbottom','stop'): '2',
         ('stop','sbottom'): '2',
         ('gluino','squark'): 'GQ',
         ('gluino','sbottom'): 'GQ',
         ('gluino','stop'): 'GQ',
         ('squark','gluino'): 'GQ',
         ('sbottom','gluino'): 'GQ',
         ('stop','gluino'): 'GQ',
         
         ('C','squark'): 'ChipmQ',
         ('C','sbottom'): 'ChipmQ',
         ('C','stop'): 'ChipmQ',
         ('squark','C'): 'ChipmQ',
         ('sbottom','C'): 'ChipmQ',
         ('stop','C'): 'ChipmQ',
         ('N','squark'): 'ChiQ',
         ('N','sbottom'): 'ChiQ',
         ('N','stop'): 'ChiQ',
         ('squark','N'): 'ChiQ',
         ('sbottom','N'): 'ChiQ',
         ('stop','N'): 'ChiQ',
         
         ('N','gluino'): 'ChiG',
         ('gluino','N'): 'ChiG',
         ('C','gluino'): 'ChipmG',
         ('gluino','C'): 'ChipmG'

}
#Chargino Chargino production
branch1 = [('','')] #branch 1 particles. format: [('vtx0_sm_finalstate','branchmother'),(vtx1_sm_finalstate,1st_intermediate),...]
branch2 = [('','')] #see above
progenitors = [('C','C'),('C','N'),('N','N'),('slepton','slepton'),('slepton','sneutrino'),('sneutrino','sneutrino'),('stau','sneutrino'),('gluino','gluino'),('squark','squark'),('sbottom','sbottom'),('stop','stop'),('squark','sbottom'),('squark','stop'),('sbottom','stop'),('gluino','squark'),('gluino','sbottom'),('gluino','stop'),('C','squark'),('C','sbottom'),('C','stop'),('N','squark'),('N','sbottom'),('N','stop'),('N','gluino'),('C','gluino')] #production mode. format: ('branch1 mother','branch2 mother')
dictkey = '' #tdict dictionary keys.
#format: ([[['branch1_vtx1_ptc1','branch1_vtx1_ptc2',...],['branch1_vtx2_ptc1',...]],[['branch2_vtx1_ptc1','branch2_vtx1_ptc2',...],['branch2_vtx2_ptc1',...]]],[[branch1_mother,branch1_intermediate1,branch1_intermediate2,...][branch2_mother,branch2_intermediate1,...]])
#e.g.: '([[[nu],[mu]],[[q],[q]]],[[C,slepton,N],[C,squark,N]])'
dictval = '' #tdict dictionary values. format: T+'branch1_mother'+'branch2_mother'+'branch1_vtx1_finalstate'+'branch1_vtx2_finalstate'+...+'branch2_vtx1_finalstate'+...
#e.g.: TChipChimnumuqq
txnames = OrderedDict() #dictionary that is written to tdict.py. Using an ordered dict for increased readability. Standard python dict would work aswell


def Fix_fs(branch1,branch2):
    """
    given a complete set of branches, create its txname and add to txnames dictionary
    param branch1: first branch finalstate and intermediates
    param branch2: second branch finalstate and intermediates
    """
    if len(branch1) == 1 and len(branch2) == 1:
        if branch1[0][1] != 'N' or branch2[0][1] != 'N': return
        dictkey = '([[[]],[[]]],[['+branch1[0][1]+'],['+branch2[0][1]+']])'#create tdict key format
        dictval = 'T'+tname[(branch1[0][1],branch2[0][1])].replace(',','')#create name
        branch1,branch2 = branch2, branch1
        invdictkey = '([[[]],[[]]],[['+branch1[0][1]+'],['+branch2[0][1]+']])' #create branch symmetric version
    elif len(branch1) == 1 and len(branch2) == 2:
        if branch1[0][1] != 'N': return
        dictkey = '([[[]],[['+branch2[1][0]+']]],[['+branch1[0][1]+'],['+branch2[0][1]+','+branch2[1][1]+']])'#create tdict key format
        dictval = 'T'+tname[(branch1[0][1],branch2[0][1])]+branch2[1][0].replace(',','').replace('photon','ga').replace('higgs','h')#create name
        branch1,branch2 = branch2, branch1
        invdictkey = '([[['+branch1[1][0]+']],[[]]],[['+branch1[0][1]+','+branch1[1][1]+'],['+branch2[0][1]+']])' #create branch symmetric version
    elif len(branch1) == 1 and len(branch2) == 3:
        if branch1[0][1] != 'N': return
        dictkey = '([[[]],[['+branch2[1][0]+'],['+branch2[2][0]+']]],[['+branch1[0][1]+'],['+branch2[0][1]+','+branch2[1][1]+','+branch2[2][1]+']])'#create tdict key format
        dictval = 'T'+tname[(branch1[0][1],branch2[0][1])]+(branch2[1][0]+branch2[2][0]).replace(',','').replace('photon','ga').replace('higgs','h')#create name
        branch1,branch2 = branch2, branch1
        invdictkey = '([[['+branch1[1][0]+'],['+branch1[2][0]+']],[[]]],[['+branch1[0][1]+','+branch1[1][1]+','+branch1[2][1]+'],['+branch2[0][1]+']])' #create branch symmetric version
    elif len(branch1) == 2 and len(branch2) == 1:
        if branch2[0][1] != 'N': return
        dictkey = '([[['+branch1[1][0]+']],[[]]],[['+branch1[0][1]+','+branch1[1][1]+'],['+branch2[0][1]+']])'#create tdict key format
        dictval = 'T'+tname[(branch1[0][1],branch2[0][1])]+(branch1[1][0]).replace(',','').replace('photon','ga').replace('higgs','h')#create name
        branch1,branch2 = branch2, branch1
        invdictkey = '([[[]],[['+branch2[1][0]+']]],[['+branch1[0][1]+'],['+branch2[0][1]+','+branch2[1][1]+']])' #create branch symmetric version
    elif len(branch1) == 3 and len(branch2) == 1:
        if branch2[0][1] != 'N': return
        dictkey = '([[['+branch1[1][0]+'],['+branch1[2][0]+']],[[]]],[['+branch1[0][1]+','+branch1[1][1]+','+branch1[2][1]+'],['+branch2[0][1]+']])'#create tdict key format
        dictval = 'T'+tname[(branch1[0][1],branch2[0][1])]+(branch1[1][0]+branch1[2][0]).replace(',','').replace('photon','ga').replace('higgs','h')#create name
        branch1,branch2 = branch2, branch1
        invdictkey = '([[[]],[['+branch2[1][0]+'],['+branch2[2][0]+']]],[['+branch1[0][1]+'],['+branch2[0][1]+','+branch2[1][1]+','+branch2[2][1]+']])' #create branch symmetric version    
    elif len(branch1) == 2 and len(branch2) == 2:#case of both branches with only 1 vertex
        dictkey = '([[['+branch1[1][0]+']],[['+branch2[1][0]+']]],[['+branch1[0][1]+','+branch1[1][1]+'],['+branch2[0][1]+','+branch2[1][1]+']])'#create tdict key format
        dictval = 'T'+tname[(branch1[0][1],branch2[0][1])]+(branch1[1][0]+branch2[1][0]).replace(',','').replace('photon','ga').replace('higgs','h')#create name
        branch1,branch2 = branch2, branch1
        invdictkey = '([[['+branch1[1][0]+']],[['+branch2[1][0]+']]],[['+branch1[0][1]+','+branch1[1][1]+'],['+branch2[0][1]+','+branch2[1][1]+']])' #create branch symmetric version
    elif len(branch1) == 2 and len(branch2) == 3:
        dictkey = '([[['+branch1[1][0]+']],[['+branch2[1][0]+'],['+branch2[2][0]+']]],[['+branch1[0][1]+','+branch1[1][1]+'],['+branch2[0][1]+','+branch2[1][1]+','+branch2[2][1]+']])'
        dictval = 'T'+tname[(branch1[0][1],branch2[0][1])]+(branch1[1][0]+branch2[1][0]+branch2[2][0]).replace(',','').replace('photon','ga').replace('higgs','h')
        branch1,branch2 = branch2, branch1
        invdictkey = '([[['+branch1[1][0]+'],['+branch1[2][0]+']],[['+branch2[1][0]+']]],[['+branch1[0][1]+','+branch1[1][1]+','+branch1[2][1]+'],['+branch2[0][1]+','+branch2[1][1]+']])'
        
    elif len(branch1) == 3 and len(branch2) == 3:
        dictkey = '([[['+branch1[1][0]+'],['+branch1[2][0]+']],[['+branch2[1][0]+'],['+branch2[2][0]+']]],[['+branch1[0][1]+','+branch1[1][1]+','+branch1[2][1]+'],['+branch2[0][1]+','+branch2[1][1]+','+branch2[2][1]+']])'
        dictval = 'T'+tname[(branch1[0][1],branch2[0][1])]+(branch1[1][0]+branch1[2][0]+branch2[1][0]+branch2[2][0]).replace(',','').replace('photon','ga').replace('higgs','h')
        branch1,branch2 = branch2,branch1
        invdictkey = '([[['+branch1[1][0]+'],['+branch1[2][0]+']],[['+branch2[1][0]+'],['+branch2[2][0]+']]],[['+branch1[0][1]+','+branch1[1][1]+','+branch1[2][1]+'],['+branch2[0][1]+','+branch2[1][1]+','+branch2[2][1]+']])'
    elif len(branch1) == 3 and len(branch2) == 2:#these should be duplicates when imposing branch symmetry
        dictkey = '([[['+branch1[1][0]+'],['+branch1[2][0]+']],[['+branch2[1][0]+']]],[['+branch1[0][1]+','+branch1[1][1]+','+branch1[2][1]+'],['+branch2[0][1]+','+branch2[1][1]+']])'
        dictval = 'T'+tname[(branch1[0][1],branch2[0][1])]+(branch1[1][0]+branch1[2][0]+branch2[1][0]).replace(',','').replace('photon','ga').replace('higgs','h')
        branch1,branch2 = branch2,branch1
        invdictkey = '([[['+branch1[1][0]+']],[['+branch2[1][0]+'],['+branch2[2][0]+']]],[['+branch1[0][1]+','+branch1[1][1]+'],['+branch2[0][1]+','+branch2[1][1]+','+branch2[2][1]+']])'
    else:
        print 'no valid branch configuration', 'b1length: ',len(branch1) ,'b2length: ',len(branch2)
        return
    txnames[dictkey] = dictval                

#    if not dictkey in txnames and not invdictkey in txnames: #no duplicates, i.e. because of branch symmetry
#        txnames[dictkey] = dictval                
            
        
    
#test branchlength.
if len(branch1)>3 or len(branch2)>3:
    print 'error: branchlength exceeded. branch1: ' + str(branch1) + ' ; branch2: '+str(branch2)

for productionmode in progenitors:
    """
    In the following, (number) designates the loop in order of occurence, while the number of - mimics the indentation. + correspond to the else path of the last if statement at the same indentation
    (1)-loop over all possible arrangements of branch progenitors, e.g. ('C','C') or ('slepton','slepton'). See list 'progenitors'
    (2)--loop over all possible numbers of vertices in FIRST branch. For now, branches can be of length 1 or 2
    (3)---select decay dictionary of last intermediate particle in the FIRST branch, then loop over all possible decays of that intermediate particle
       ----if the vertex/intermediate selected is the last in the cascade (before the lsp) and the decay selected does not end in a neutralino, continue to next decaymode
       ----append the decaymode to the FIRST branch
    (4)----if the number of vertices allows for another vertex to be added to the FIRST branch, select decay dictionary of last intermediate particle in the FIRST branch, then loop over all possible decays of that intermediate particle
       -----if the vertex/intermediate selected is the last in the cascade (before the lsp) and the decay selected does not end in a neutralino, continue to next decaymode #for now, this is always the case as the maximum branchlength is 2
       -----append the decaymode to the FIRST branch
    (5)-----loop over all possible numbers of vertices in SECOND branch.
    (6)------select decay dictionary of last intermediate particle in the SECOND branch, then loop over all possible decays of that intermediate particle
       -------if the vertex/intermediate selected is the last in the cascade (before the lsp) and the decay selected does not end in a neutralino, continue to next decaymode
       -------append the decaymode to the SECOND branch
    (7)-------if the number of vertices allows for another vertex to be added to the SECOND branch, select decay dictionary of last intermediate particle in the SECOND branch, then loop over all possible decays of that intermediate particle
       --------if the vertex/intermediate selected is the last in the cascade (before the lsp) and the decay selected does not end in a neutralino, continue to next decaymode in loop (7)
       --------append the decaymode to the SECOND branch
       --------call Fix_fs(first branch,second branch)
       --------remove the last element of the SECOND branch
       --------go to next element of loop (7)
       -------remove the last element of the SECOND branch
       -------go to next element of loop (6)
       +++++++call Fix_fs(first branch,second branch)
       +++++++remove the last element of the SECOND branch
       +++++++go to next element of loop (6)
       ------go to next element of loop (5)
       -----remove the last element of the FIRST branch
       -----go to next element of loop (4)
       ----remove the last element of the FIRST branch
       ++++go to loop (5), ignore loop (4) and line directly above this one
       ----go to next element of loop (3)
       ---go to next element of loop (2)
       --go to next element of loop (1)

    

    #for now, this script only goes to a branchlength of 2
    #for now, this script only works for electroweak branch progenitors
    """
    #FIXME: include zero vertex branches!
    #better implementation: make 'create_branch' function that creates branches independently, then recombine all permutations of branches.
    
    #loop (1)
    branch1 = [('none',productionmode[0])]
    branch2 = [('none',productionmode[1])]
    #how to select decays to lsp? if not Xdecays[sparticle] == 'N': continue
    for b1vertexnr in range(3):#loop over amount of vertices for branch 1.
        if b1vertexnr == 0:
            if productionmode[0] != 'N':
                continue
        for b2vertexnr in range(3):#branch 2 can have 1 or 2 vertices
            #loop (5)
            if b2vertexnr == 0:
                if productionmode[1] != 'N':
                    continue
                Fix_fs(branch1,branch2)
                continue
            for b2decay in whatdecay[branch2[-1][1]]:#same as branch1
                #loop (6)
                if b2vertexnr == 1 and b2decay[1] != 'N':
                    continue
                branch2.append(b2decay)
                if b2vertexnr == 1:
                    Fix_fs(branch1,branch2)#fix finalstate and add to dict
                    branch2.pop()
                    continue
                if len(branch1)>3 or len(branch2)>3:#test branchlength
                    print 'error: branchlength exceeded. branch1: ' + str(branch1) + ' ; branch2: '+str(branch2)
                if b2vertexnr == 2:#consider cases with 2 vertices in branch2
                    for b2v2decay in whatdecay[branch2[-1][1]]:
                        #loop (7)
                        if b2v2decay[1] != 'N':#only consider decays ending in neutralinos
                            continue
                        branch2.append(b2v2decay)
                        if len(branch1)>3 or len(branch2)>3:#test branchlength
                            print 'error: branchlength exceeded. branch1: ' + str(branch1) + ' ; branch2: '+str(branch2)
                        Fix_fs(branch1,branch2)#fix the finalstate and add to dict
                        branch2.pop()
                    branch2.pop()
        #loop (2)
        for b1decay in whatdecay[branch1[-1][1]]:#selects the decay dictionary to loop over, then loops over it. branch1[-1][1] looks at last intermediate in branch1
            #loop (3)
            if b1vertexnr == 1 and b1decay[1] != 'N':#if last vertex, only consider decays ending in neutralinos
                #possible alternative if statement: if b1vertexnr-len(branch1) == 0 and b1decay[-1] != 'N': continue
                continue
            if b1vertexnr != 0:
                branch1.append(b1decay) #add the decay to the branch
            if len(branch1)>3 or len(branch2)>3:#test branchlength
                print 'error: branchlength exceeded. branch1: ' + str(branch1) + ' ; branch2: '+str(branch2)
            if b1vertexnr == 2:#if there is another vertex, go through all possible decays for the 2nd vertex. Only consider decays ending in neutralinos
                for b1v2decay in whatdecay[branch1[-1][1]]:
                    #loop (4)
                    if b1v2decay[1] != 'N':#only consider decays ending in neutralinos, as this is the last vertex
                        continue
                    branch1.append(b1v2decay) #add the decay ending in a neutralino to the branch
                    if len(branch1)>3 or len(branch2)>3:#test branchlength
                        print 'error: branchlength exceeded. branch1: ' + str(branch1) + ' ; branch2: '+str(branch2)
                    #do branch2 and set finalstate
                    for b2vertexnr in range(3):#branch 2 can have 1 or 2 vertices
                        #loop (5)
                        if b2vertexnr == 0:
                            if productionmode[1] != 'N':
                                continue
                            Fix_fs(branch1,branch2)
                            continue
                        for b2decay in whatdecay[branch2[-1][1]]:#same as branch1
                            #loop (6)
                            if b2vertexnr == 1 and b2decay[1] != 'N':
                                continue
                            branch2.append(b2decay)
                            if b2vertexnr == 1:
                                Fix_fs(branch1,branch2)#fix finalstate and add to dict
                                branch2.pop()
                                continue
                            if len(branch1)>3 or len(branch2)>3:#test branchlength
                                print 'error: branchlength exceeded. branch1: ' + str(branch1) + ' ; branch2: '+str(branch2)
                            if b2vertexnr == 2:#consider cases with 2 vertices in branch2
                                for b2v2decay in whatdecay[branch2[-1][1]]:
                                    #loop (7)
                                    if b2v2decay[1] != 'N':#only consider decays ending in neutralinos
                                        continue
                                    branch2.append(b2v2decay)
                                    if len(branch1)>3 or len(branch2)>3:#test branchlength
                                        print 'error: branchlength exceeded. branch1: ' + str(branch1) + ' ; branch2: '+str(branch2)
                                    Fix_fs(branch1,branch2)#fix the finalstate and add to dict
                                    branch2.pop()
                                branch2.pop()
                    branch1.pop() #at this point, all possibilities stemming from the decay chosen for branch1 have been considered. remove last element of branch one and go to next element of the loop
                branch1.pop()
            if b1vertexnr ==1:#case of only 1 vertex in branch1
                #do branch2, set finalstate
                for b2vertexnr in range(3):
                    if b2vertexnr == 0:
                        if productionmode[1] != 'N':
                            continue
                        else:
                            Fix_fs(branch1,branch2)
                            continue
                    for b2decay in whatdecay[branch2[-1][1]]:
                        if b2vertexnr == 1 and b2decay[1] != 'N':
                            continue
                        branch2.append(b2decay)
                        if len(branch1)>3 or len(branch2)>3:#test branchlength
                            print 'error: branchlength exceeded. branch1: ' + str(branch1) + ' ; branch2: '+str(branch2)
                        if b2vertexnr == 2:
                            for b2v2decay in whatdecay[branch2[-1][1]]:
                                if b2v2decay[1] != 'N':
                                    continue
                                branch2.append(b2v2decay)
                                if len(branch1)>3 or len(branch2)>3:#test branchlength
                                    print 'error: branchlength exceeded. branch1: ' + str(branch1) + ' ; branch2: '+str(branch2)
                                Fix_fs(branch1,branch2)#fix the finalstate and add to dict
                                branch2.pop()
                            branch2.pop()
                        else:
                            Fix_fs(branch1,branch2)#fix the finalstate and add to dict
                            branch2.pop()


                branch1.pop()#all possibilities of branchlength 1 in 1st branch stemming from chosen decay have been done, go to next decay in the loop


#simplified models from smodels website and manual additions
smstxnames = {"([[[q,q]],[[q,q]]],[[gluino,N],[gluino,N]])": 'T1',
              "([[[b,b]],[[b,b]]],[[gluino,N],[gluino,N]])": 'T1bbbb',
              "([[[b,b]],[[b,t]]],[[gluino,N],[gluino,N]])": 'T1bbbt',
              "([[[b,b]],[[t,b]]],[[gluino,N],[gluino,N]])": 'T1bbbt',
              "([[[b,b]],[[q,q]]],[[gluino,N],[gluino,N]])": 'T1bbqq',
              "([[[b,b]],[[t,t]]],[[gluino,N],[gluino,N]])": 'T1bbtt',
              "([[[b,t]],[[b,t]]],[[gluino,N],[gluino,N]])": 'T1btbt',
              "([[[t,b]],[[b,t]]],[[gluino,N],[gluino,N]])": 'T1btbt',
              "([[[b,t]],[[t,b]]],[[gluino,N],[gluino,N]])": 'T1btbt',
              "([[[t,b]],[[t,b]]],[[gluino,N],[gluino,N]])": 'T1btbt',
              "([[[b,t]],[[q,q]]],[[gluino,N],[gluino,N]])": 'T1btqq',
              "([[[t,b]],[[q,q]]],[[gluino,N],[gluino,N]])": 'T1btqq',
              "([[[b,t]],[[t,t]]],[[gluino,N],[gluino,N]])": 'T1bttt',
              "([[[t,b]],[[t,t]]],[[gluino,N],[gluino,N]])": 'T1bttt',
              "([[[t,t]],[[q,q]]],[[gluino,N],[gluino,N]])": 'T1ttqq',
              "([[[t,t]],[[t,t]]],[[gluino,N],[gluino,N]])": 'T1tttt',
              "([[[toff,toff]],[[toff,toff]]],[[gluino,N],[gluino,N]])": 'T1ttttoff',
              "([[[q]],[[q]]],[[squark,N],[squark,N]])": 'T2',
              "([[[b]],[[b]]],[[squark,N],[squark,N]])": 'T2bb',
              "([[[b,W]],[[b,W]]],[[squark,N],[squark,N]])": 'T2bbWW', "([[[W,b]],[[b,W]]],[[squark,N],[squark,N]])": 'T2bbWW', "([[[b,W]],[[W,b]]],[[squark,N],[squark,N]])": 'T2bbWW',"([[[W,b]],[[W,b]]],[[squark,N],[squark,N]])": 'T2bbWW', #these are all permutations of the two b,W vertices
              "([[[b,Woff]],[[b,Woff]]],[[squark,N],[squark,N]])": 'T2bbWWoff', "([[[Woff,b]],[[b,Woff]]],[[squark,N],[squark,N]])": 'T2bbWWoff', "([[[b,Woff]],[[Woff,b]]],[[squark,N],[squark,N]])": 'T2bbWWoff', "([[[Woff,b]],[[Woff,b]]],[[squark,N],[squark,N]])": 'T2bbWWoff',#same as above with b,Woff
              "([[[b]],[[t]]],[[squark,N],[squark,N]])": 'T2bt',
              "([[[c]],[[c]]],[[squark,N],[squark,N]])": 'T2cc',
              "([[[t]],[[t]]],[[squark,N],[squark,N]])": 'T2tt',
              "([[[toff]],[[toff]]],[[squark,N],[squark,N]])": 'T2ttoff',
              "([[[q,q],[W]],[[q,q],[W]]],[[gluino,C,N],[gluino,C,N]])": 'T5WW',
              "([[[q,q],[Woff]],[[q,q],[Woff]]],[[gluino,C,N],[gluino,C,N]])": 'T5WWoff',
              "([[[q,q],[Z]],[[q,q],[Z]]],[[gluino,N,N],[gluino,N,N]])": 'T5ZZ',
              "([[[q,q],[Zoff]],[[q,q],[Zoff]]],[[gluino,N,N],[gluino,N,N]])": 'T5ZZoff',
              "([[[b],[b]],[[b],[b]]],[[gluino,squark,N],[gluino,squark,N]])": 'T5bbbb',
              "([[[b],[b]],[[b],[t]]],[[gluino,squark,N],[gluino,squark,N]])": 'T5bbbt',
              "([[[b],[b]],[[t],[b]]],[[gluino,squark,N],[gluino,squark,N]])": 'T5bbtb',
              "([[[b],[t]],[[b],[t]]],[[gluino,squark,N],[gluino,squark,N]])": 'T5btbt',
              "([[[t],[b]],[[t],[b]]],[[gluino,squark,N],[gluino,squark,N]])": 'T5tbtb',
              "([[[t],[b]],[[t],[t]]],[[gluino,squark,N],[gluino,squark,N]])": 'T5tbtt',
              "([[[t],[c]],[[t],[c]]],[[gluino,squark,N],[gluino,squark,N]])": 'T5tctc',
              "([[[t],[t]],[[t],[t]]],[[gluino,squark,N],[gluino,squark,N]])": 'T5tttt',
              "([[[toff],[toff]],[[toff],[toff]]],[[gluino,squark,N],[gluino,squark,N]])": 'T5ttttoff',
              "([[[q],[W]],[[q],[W]]],[[squark,C,N],[squark,C,N]])": 'T6WW',
              "([[[q],[Woff]],[[q],[Woff]]],[[squark,C,N],[squark,C,N]])": 'T6WWoff',
              "([[[Z],[t]],[[Z],[t]]],[[squark,squark,N],[squark,squark,N]])": 'T6ZZtt',
              "([[[b],[W]],[[b],[W]]],[[squark,C,N],[squark,C,N]])": 'T6bbWW',
              "([[[b],[Woff]],[[b],[Woff]]],[[squark,C,N],[squark,C,N]])": 'T6bbWWoff',
              "([[[t],[W]],[[t],[W]]],[[squark,C,N],[squark,C,N]])": 'T6ttWW',
              "([[[t],[Woff]],[[t],[Woff]]],[[squark,C,N],[squark,C,N]])": 'T6ttWWoff',
              "([[[e],[e]],[[e],[e]]],[[N,slepton,N],[N,slepton,N]])": 'TChiChiSlepSlep',
              "([[[mu],[mu]],[[mu],[mu]]],[[N,slepton,N],[N,slepton,N]])": 'TChiChiSlepSlep',
              "([[[e],[e]],[[mu],[mu]]],[[N,slepton,N],[N,slepton,N]])": 'TChiChiSlepSlep',
              "([[[L],[L]],[[L],[nu]]],[[N,slepton,N],[C,sneutrino,N]])": 'TChiChipmSlepL',
              "([[[L],[L]],[[nu],[L]]],[[N,slepton,N],[C,slepton,N]])": 'TChiChipmSlepL',
              "([[[L],[L]],[[nu],[ta]]],[[N,slepton,N],[C,stau,N]])": 'TChiChipmSlepStau',
              "([[[ta],[ta]],[[nu],[ta]]],[[N,stau,N],[C,stau,N]])": 'TChiChipmStauStau',
              "([[[ta],[ta]],[[ta],[nu]]],[[N,stau,N],[C,sneutrino,N]])": 'TChiChipmStauL',
              "([[[W]],[[higgs]]],[[C,N],[N,N]])": 'TChiWH',
              "([[[W]],[[W]]],[[C,N],[C,N]])": 'TChiWW',
              "([[[Woff]],[[Woff]]],[[C,N],[C,N]])": 'TChiWWoff',
              "([[[W]],[[Z]]],[[C,N],[N,N]])": 'TChiWZ',
              "([[[Woff]],[[Zoff]]],[[C,N],[N,N]])": 'TChiWZoff',
              "([[[L],[nu]],[[nu],[L]]],[[C,sneutrino,N],[C,slepton,N]])": 'TChipChimSlepSnu', "([[[L],[nu]],[[L],[nu]]],[[C,sneutrino,N],[C,sneutrino,N]])": 'TChipChimSlepSnu', "([[[nu],[L]],[[nu],[L]]],[[C,slepton,N],[C,slepton,N]])": 'TChipChimSlepSnu', #this name is odd, only one process contains both slepton and sneutrino. also: should add electron and muon seperately?
              "([[[ta],[nu]],[[nu],[ta]]],[[C,sneutrino,N],[C,stau,N]])": 'TChipChimStauSnu',
              "([[[ta],[nu]],[[ta],[nu]]],[[C,sneutrino,N],[C,sneutrino,N]])": 'TChipChimStauSnu',
              "([[[nu],[ta]],[[nu],[ta]]],[[C,stau,N],[C,stau,N]])": 'TChipChimStauSnu',#change to SnuStau?
              "([[[e]],[[e]]],[[slepton,N],[slepton,N]])": 'TSlepSlep', "([[[mu]],[[mu]]],[[slepton,N],[slepton,N]])": 'TSlepSlep',
              "([[[jet]],[[jet,jet]]],[[squark,N],[gluino,N]])": 'TGQ', "([[[q]],[[q,q]]],[[squark,N],[gluino,N]])": 'TGQ',
              "([[[jet]],[[b,b]]],[[squark,N],[gluino,N]])": 'TGQbbq', "([[[q]],[[b,b]]],[[squark,N],[gluino,N]])": 'TGQbbq',
              "([[[jet]],[[b,t]]],[[squark,N],[gluino,N]])": 'TGQbtq', "([[[q]],[[b,t]]],[[squark,N],[gluino,N]])": 'TGQbtq',
              "([[[jet]],[[t,t]]],[[squark,N],[gluino,N]])": 'TGQttq', "([[[q]],[[t,t]]],[[squark,N],[gluino,N]])": 'TGQttq',
              "([[[c]],[[c]]],[[squark,N],[squark,N]])": 'TScharm',


              #manual additions
              "([[[q],[q]],[[q],[q]]],[[gluino,squark,N],[gluino,squark,N]])": 'TGGqqqq',
              "([[[q,q]],[[q],[Zoff]]],[[gluino,N],[squark,N,N]])": 'TGGqqqZoff',
              "([[[q,q]],[[q],[Woff]]],[[gluino,N],[squark,C,N]])": 'TGGqqqWoff'


}



#for key in smstxnames.keys(): #add txnames from smodels dictionary if not already contained under the new naming scheme
#    if key not in txnames:
#        txnames[key] = smstxnames[key]
with open('./smodels/tools/tdict.py','w') as tdict:
    tdict.write('from collections import OrderedDict \n')
    tdict.write('txnames = ')
    tdict.write(str(txnames))
#print 'tdict: ',txnames
print '#entries in tdict: ',len(txnames)
        
