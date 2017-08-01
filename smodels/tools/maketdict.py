from collections import OrderedDict
import os
q = {'q': 'squark', 'c': 'squark', 'b':'sbottom','t':'stop','toff':'stop'}
l = {'e': 'slepton', 'mu': 'slepton','ta':'stau','nu':'sneutrino'}
b = ['Z','Zoff','W','Woff']

Cdecays = {('q',q['q']):'q',('q',q['c']):'q',('q',q['b']):'q',('q',q['t']):'q',('c',q['q']):'c',('c',q['b']):'c',('c',q['t']):'c',('b',q['t']):'b',('t',q['b']):'t',('toff',q['b']):'toff',#quark vertices
           ('e','sneutrino'):'l',('mu','sneutrino'):'l',('ta','sneutrino'):'ta',#lepton vertices
           ('nu','slepton'):'nu',('nu','stau'):'nu', #neutrino vertices
           ('Z','C'):'Z',('Zoff','C'):'Zoff',#Z vertices
           ('W','N'):'W',('Woff','N'):'Woff'#W vertices
}
Ndecays = {('q',q['q']):'q',('c',q['c']):'c',('b',q['b']):'b',('t',q['t']):'t',('toff',q['toff']):'toff', #quark decays
           ('Z','N'):'Z',('Zoff','N'):'Zoff',#Z decays
           ('W','C'):'W',('Woff','C'):'Woff' #W decays
}
#only interested in decays to lsp for quarks -> trivial (Q,N) and (c,N)
Sqdecays = {('q','N'):'q',('c','N'):'c'}
#Scdecays = {('c','N'):'c'} scharms not implemented in smodels
Sbdecays = {('b','N'):'b'}
Stdecays = {('t','N'):'t',('toff','N'):'toff'}


Sldecays = {('e','N'):'l',('mu','N'):'l',#to neutralino
            ('nu','C'):'nu'#to chargino
}
Staudecays = {('ta','N'):'ta',#to neutralino
              ('nu','C'):'nu'#to chargino
}
Snudecays = {('nu','N'):'nu',#to neutralino
             ('e','C'):'l',('mu','C'):'mu',('ta','C'):'ta',#to chargino
}
#dictionary assigning the decays to use to the sparticle in question
whatdecay = {'squark': Sqdecays,
             'sbottom': Sbdecays,
             'stop': Stdecays,
             'slepton':Sldecays,
             'stau': Staudecays,
             'sneutrino': Snudecays,
             'C': Cdecays,
             'N': Ndecays,
}
#dictionary to assign Tname to a given productionmode
tname = {('N','N'): 'ChiChi',
         ('C','C'): 'ChipChim',
         ('C','N'): 'ChiChipm',
         ('N','C'): 'ChiChipm',
         ('slepton','slepton'): 'SlepSlep'
}
#loop over 1st branch, loop over vertices, loop over nr of vertices
#Chargino Chargino production
branch1 = [('none','C')]
branch2 = [('none','C')]
progenitors = [('C','C'),('C','N'),('N','N'),('slepton','slepton')]
dictkey = ''
dictval = ''
txnames = OrderedDict()


def Fix_fs(branch1,branch2):
    if len(branch1) == 2 and len(branch2) == 2:#case of both branches with only 1 vertex
        dictkey = '([[[' +branch1[1][0]+']],[['+branch2[1][0]+']]],[['+branch1[0][1]+','+branch1[1][1]+'],['+branch2[0][1]+','+branch2[1][1]+']])'#create tdict key format
#        dictval = 'TChipChim'+branch1[1][0]+branch2[1][0]#create name
        dictval = 'T'+tname[(branch1[0][1],branch2[0][1])]+branch1[1][0]+branch2[1][0]#create name
    elif len(branch1) == 2 and len(branch2) == 3:
        dictkey = '([[[' +branch1[1][0]+']],[['+branch2[1][0]+'],['+branch2[2][0]+']]],[['+branch1[0][1]+','+branch1[1][1]+'],['+branch2[0][1]+','+branch2[1][1]+','+branch2[2][1]+']])'
        dictval = 'T'+tname[(branch1[0][1],branch2[0][1])]+branch1[1][0]+branch2[1][0]+branch2[2][0]
    elif len(branch1) == 3 and len(branch2) == 3:
        dictkey = '([[[' +branch1[1][0]+'],['+branch1[2][0]+']],[['+branch2[1][0]+'],['+branch2[2][0]+']]],[['+branch1[0][1]+','+branch1[1][1]+','+branch1[2][1]+'],['+branch2[0][1]+','+branch2[1][1]+','+branch2[2][1]+']])'
        dictval = 'T'+tname[(branch1[0][1],branch2[0][1])]+branch1[1][0]+branch1[2][0]+branch2[1][0]+branch2[2][0]
        """    elif len(branch2) == 2 and len(branch1) == 3:#these should be duplicates when imposing branch symmetry
        dictkey = '([[[' +branch1[1][0]+'],['+branch1[2][0]+']],[['+branch2[1][0]+']]],[['+branch1[0][1]+','+branch1[1][1]+','+branch1[2][1]+'],['+branch2[0][1]+','+branch2[1][1]+']])'
        dictval = 'T'+tname[(branch1[0][1],branch2[0][1])]+branch1[1][0]+branch1[2][0]+branch2[1][0]
        """
    else:
#        print 'no case found, should only be duplicates when considering branch symmetry'
        return
    if not dictkey in txnames: #no duplicates, i.e. because of branch symmetry
        txnames[dictkey] = dictval                
            
        
    

if len(branch1)>3 or len(branch2)>3:#test branchlength
    print 'error: branchlength exceeded. branch1: ' + str(branch1) + ' ; branch2: '+str(branch2)

for productionmode in progenitors:
    branch1 = [('none',productionmode[0])]
    branch2 = [('none',productionmode[1])]
    #how to select decays to lsp? if not Xdecays[sparticle] == 'N': continue
    for b1vertexnr in range(1,3):#loop over amount of vertices for branch 1.
        for b1decay in whatdecay[branch1[-1][1]]:#selects the decay dictionary to loop over, then loops over it. branch1[-1][1] looks at last intermediate in branch1
            if b1vertexnr == 1 and b1decay[1] != 'N':#if last vertex, only consider decays ending in neutralinos
                continue
            branch1.append(b1decay) #add the decay to the branch
            if len(branch1)>3 or len(branch2)>3:#test branchlength
                print 'error: branchlength exceeded. branch1: ' + str(branch1) + ' ; branch2: '+str(branch2)
            if b1vertexnr == 2:#if there is another vertex, go through all possible decays for the 2nd vertex. Only consider decays ending in neutralinos
                for b1v2decay in whatdecay[branch1[-1][1]]:
                    if b1v2decay[1] != 'N':#only consider decays ending in neutralinos, as this is the last vertex
                        continue
                    branch1.append(b1v2decay) #add the decay ending in a neutralino to the branch
                    if len(branch1)>3 or len(branch2)>3:#test branchlength
                        print 'error: branchlength exceeded. branch1: ' + str(branch1) + ' ; branch2: '+str(branch2)
                    #do branch2, set finalstate
                    for b2vertexnr in range(1,3):#branch 2 can have 1 or 2 vertices
                        for b2decay in whatdecay[branch2[-1][1]]:#same as branch1
                            if b2vertexnr == 1 and b2decay[1] != 'N':
                                continue
                            branch2.append(b2decay)
                            if len(branch1)>3 or len(branch2)>3:#test branchlength
                                print 'error: branchlength exceeded. branch1: ' + str(branch1) + ' ; branch2: '+str(branch2)
                            if b2vertexnr == 2:#consider cases with 2 vertices in branch2
                                for b2v2decay in whatdecay[branch2[-1][1]]:
                                    if b2v2decay[1] != 'N':#only consider decays ending in neutralinos
                                        continue
                                    branch2.append(b2v2decay)
                                    if len(branch1)>3 or len(branch2)>3:#test branchlength
                                        print 'error: branchlength exceeded. branch1: ' + str(branch1) + ' ; branch2: '+str(branch2)
                                    Fix_fs(branch1,branch2)#fix the finalstate and add to dict
                                    branch2.pop()
                                branch2.pop()
                            else:#case of only 1 vertex in branch2
                                Fix_fs(branch1,branch2)#fix finalstate and add to dict
                                branch2.pop()

                    branch1.pop() #at this point, all possibilities stemming from the decay chosen for branch1 have been considered. remove last element of branch one and go to next element of the loop
                branch1.pop()
            else:#case of only 1 vertex in branch1
                #do branch2, set finalstate
                for b2vertexnr in range(1,3):
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



for key in smstxnames.keys(): #add txnames from smodels dictionary if not already contained under the new naming scheme
    if key not in txnames:
        txnames[key] = smstxnames[key]
with open('./smodels/tools/tdict.py','w') as tdict:
    tdict.write('from collections import OrderedDict \n')
    tdict.write('txnames = ')
    tdict.write(str(txnames))
#print 'tdict: ',txnames
print '#entries in tdict: ',len(txnames)
        
