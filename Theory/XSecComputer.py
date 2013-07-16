#!/usr/bin/env python

"""
.. module:: XSecComputer
    :synopsis: The unit responsible for the computation of reference ("theory") \
      production cross sections
    
.. moduleauthor:: Suchita Kulkarni <suchita.kulkarni@gmail.com>
    
"""

def loFromLHE( lhefile, totalxsec, nevts=None ):
  """ compute LO weights for each production process from LHE file.

  :param lhefile: name of the lhe file
  :type lhefile: str
  :param totalxsec: total cross section, in fb. If the total cross section can be \
    obtained from the lhe file (from the madgraph banner), then set totalxsec=None
    to pick up the lhe cross section.
  :type totalxsec: cross section 
  :param nevts: maximum number of events to read. None means 'read all'.
  :returns: an array of dictionaries: weights, xsecs, nevts
  """
  from Theory import LHEReader
  import  types
  from Tools.PhysicsUnits import addunit
  #Get event decomposition:
  n_evts={}
  reader = LHEReader.LHEReader( lhefile, nevts )
  ntrueevents=0
  for event in reader:
    ntrueevents+=1
    mompdg = event.getMom()    
    if not mompdg: continue
    getprodcs(mompdg[0], mompdg[1], n_evts)

  ##print "reader metainfo=",reader.metainfo
  if type(totalxsec)==types.NoneType:
    if not reader.metainfo.has_key ( "totalxsec" ):
      print "[XSecComputer.py] error: totalxsec=None, but no xsec can be picked up from lhe reader"
      return None
    else:
      totalxsec=reader.metainfo["totalxsec"]

  weight, sigma = {}, {}
  # print "[XSecComputer] lhe",lhefile
  for (key,xsec) in n_evts.items():
    weight[key]= totalxsec / float(ntrueevents) # weight for one event
    sigma[key]=xsec * totalxsec / float(ntrueevents) # production cross-section
    #print "[XSecComputer] moms=%s n=%d ntot=%d w=%s" % ( key,xsec,nevts, weight[key] )

  return [ weight, sigma, n_evts ]
    

def compute(nevts,slhafile,rpythia = True, donlo = True, basedir=None,datadir=None):
  """ Runs pythia at 7 and 8 TeV and compute weights for each production process. 

  :param basedir: directory base. If None, then the we look for the SMSDecomposition \
    directory in the current working directory. nllfast we expect to be in \
    basedir+"/nllfast", the template config we expect to reside in basedir+"/etc"
  :type basedir: str
  :param runpythia: run pythia. If False, read old fort_8,7.68 files and assumes \
    total xsec = 1 (only useful for fast debugging) 
  :returns: a dictionary with weights at 7 and 8 TeV and the event file to be used \
     for SMS decomposition.
  
  """

  import shutil
  from Theory import NLLXSec, CrossSection, LHEReader
  from Tools.PhysicsUnits import addunit
  import os, sys

  if basedir==None:
    basedir=os.getcwd()
    if basedir[-3:]=="bin": basedir=basedir[:-3]
    if basedir[-4:]=="test": basedir=basedir[:-4]
    if basedir[-10:]=="regression": basedir=basedir[:-10]
  if datadir==None:
    datadir=basedir+"/data"
  if not os.path.exists ( datadir ):
    print "[XSecComputer.py] directory",datadir,"does not exist. Please create."
    return None
    
  nllbase=basedir+"/nllfast"
  if donlo and not os.path.isdir ( nllbase ):
    print "[XSecComputer] error: %s does not exist or is not a directory." % nllbase
    sys.exit(0)
  if donlo and not os.path.isfile ( slhafile ):
    print "[XSecComputer] error: %s does not exist or is not a file." % slhafile
    sys.exit(0)
  installdir=basedir
  etcdir="%s/etc/" % basedir
  
  #LHE event file
  lhefile = "%s/fort_8.68" % datadir
  lhe7file = "%s/fort_7.68" % datadir
  lhe8file = "%s/fort_8.68" % datadir
  if rpythia:
#run pythia at 8 TeV:
    D = runPythia( slhafile,nevts,8,
                   datadir=datadir,etcdir=etcdir,installdir=installdir)
    shutil.copy2("%s/fort.68" % datadir, lhe8file )
    total_cs8 = addunit(D["xsecfb"],'fb')
  
#run pythia at 7 TeV:
    D = runPythia(slhafile,nevts,7,
                   datadir=datadir,etcdir=etcdir,installdir=installdir)

    shutil.copy2("%s/fort.68" % datadir, lhe7file )
    total_cs7 = addunit(D["xsecfb"],'fb')
  else:
    total_cs8 = addunit(1.,'fb')
    total_cs7 = addunit(1.,'fb')

  weight_8, sigma_8, n8_evts = loFromLHE ( lhe8file, total_cs8, nevts )
#Get 7 TeV event decomposition:
  n7_evts={}
  reader = LHEReader.LHEReader( lhe7file,nevts)
  for event in reader:
    mompdg = event.getMom()
    getprodcs(mompdg[0], mompdg[1], n7_evts)

  weight_7 = {}
  sigma_7 = {}
  for key in n7_evts.keys():
    if n8_evts.has_key(key):
      weight_7[key]=n7_evts[key]*total_cs7/(nevts*n8_evts[key])
      sigma_7[key]=n7_evts[key]*total_cs7/nevts # Production cross-section

  #Make sure both dictionaries have the same number of entries
  for key in sigma_7.keys() + sigma_8.keys():
    if not sigma_7.has_key(key): 
      sigma_7[key]=addunit(0.,'fb')
      weight_7[key]=addunit(0.,'fb')
    if not sigma_8.has_key(key): 
      sigma_8[key]=addunit(0.,'fb')
      weight_8[key]=addunit(0.,'fb')

  #Get NLO cross-sections from NLLfast:
  if donlo:
    sigma_8NLO = {}
    sigma_7NLO = {}
    weight_8NLO = {}
    weight_7NLO = {}

    for key in sigma_8.keys():

      nllres = NLLXSec.getNLLresult(key[0],key[1],slhafile,base=nllbase)
      k7 = 1.
      k8 = 1.
   
      if nllres[0]['K_NLL_7TeV'] and nllres[0]['K_NLO_7TeV']:
        k7 = nllres[0]['K_NLL_7TeV']*nllres[0]['K_NLO_7TeV']
      elif nllres[0]['K_NLO_7TeV']:
        k7 = nllres[0]['K_NLO_7TeV']
      if nllres[1]['K_NLL_8TeV'] and nllres[1]['K_NLO_8TeV']:
        k8 = nllres[1]['K_NLL_8TeV']*nllres[1]['K_NLO_8TeV']
      elif nllres[1]['K_NLO_8TeV']:
        k8 = nllres[1]['K_NLO_8TeV']

      LO7 = weight_7[key]
      LO8 = weight_8[key]
      NLO7 = LO7*k7
      NLO8 = LO8*k8
      weight_7NLO[key]=NLO7
      weight_8NLO[key]=NLO8

      LO7 = sigma_7[key]
      LO8 = sigma_8[key]
      NLO7 = LO7*k7
      NLO8 = LO8*k8
      sigma_7NLO[key]=NLO7
      sigma_8NLO[key]=NLO8


#Weight and production cross-section dictionaries (NLL = NLO+NLL)
  Wdic = {'7 TeV (LO)':weight_7, '8 TeV (LO)':weight_8}
  Xsecdic = {'7 TeV (LO)':sigma_7, '8 TeV (LO)':sigma_8}
  if donlo:
    Wdic.update({'7 TeV (NLL)':weight_7NLO, '8 TeV (NLL)':weight_8NLO})
    Xsecdic.update({'7 TeV (NLL)':sigma_7NLO, '8 TeV (NLL)':sigma_8NLO})

#Weight center of mass energies dictionary
  CMdic = {'7 TeV (LO)': addunit(7.,'TeV'), '8 TeV (LO)': addunit(8.,'TeV')}
  if donlo:
    CMdic.update({'7 TeV (NLL)': addunit(7.,'TeV'), '8 TeV (NLL)': addunit(8.,'TeV')})
  return CrossSection.CrossSection ( {"Wdic" : Wdic, "lhefile" : lhefile, "lhe7file" : lhe7file, "lhe8file": lhe8file, "Xsecdic" : Xsecdic, "CMdic" : CMdic} )
  
  

def getprodcs(pdgm1, pdgm2, sigma):  
  if pdgm1 > pdgm2: 
    pdgm1, pdgm2 = pdgm2 , pdgm1
  newkey=(pdgm1,pdgm2) 
  if not sigma: 
    init={newkey:1}
    sigma.update(init)
    return sigma
  if not sigma.has_key(newkey):
    sigma[newkey]=0
  sigma[newkey]+=1
  
  return sigma

def runPythia ( slhafile, n, sqrts=7, datadir="./data/", etcdir="./etc/",
                installdir="./" ):
  """ run pythia_lhe with n events, at sqrt(s)=sqrts.

    :param slhafile: inputfile
    :type slhafile: str
    :param datadir: directory where this all should run
    :param etcdir: is where external_lhe.template is to be picked up
    :param installdir: is where pythia_lhe is to be found.  
  """
  import commands, os, sys
  # print "[SMSXSecs.runPythia] try to run pythia_lhe at sqrt(s)=%d with %d events" % (sqrts,n)
  o=commands.getoutput ( "cp %s %s/fort.61" % ( slhafile, datadir ) )
  if len(o)>0:
    print "[SMSXSecs.py] runPythia error",o
  f=open(etcdir+"/external_lhe.template") 
  lines=f.readlines()
  f.close()
  g=open(datadir+"/external_lhe.dat","write")
  for line in lines:
    out=line.replace("NEVENTS",str(n)).replace("SQRTS",str(1000*sqrts))
    g.write ( out )
  g.close()
  if not os.path.isdir( datadir ):
    print "[XSecComputer.py] error: %s does not exist or is not a directory." % datadir
    sys.exit(0)
  executable="%s/pythia_lhe" % installdir
  if not os.path.isfile ( executable ) or not os.access(executable,os.X_OK):
    print "[XSecComputer.py] error: %s does not exist." % executable
    sys.exit(0)
  if not os.path.isfile ( "%s/external_lhe.dat" % datadir ):
    print "[XSecComputer.py] error: %s/external_lhe.dat does not exist." % datadir
    sys.exit(0)
  o=commands.getoutput ( "cd %s; %s < external_lhe.dat" % \
     ( datadir, executable ) )
  lines=o.split( "\n" )
  xsecfb=None
  for line in lines:
#    print line
    if line.find("All included subprocesses")>0:
      try:
        xsecfb=float(line[67:78].replace("D","E"))*10**12
      except Exception,e:
        print "[ResultsTables.py] Exception",e,"xsecfb=",line[67:78]
        print "  `-- line=",line
#        print "  `-- masterkey=",masterkey
  return { "xsecfb": xsecfb }

def clean ( datadir ):
  """ simple routine that can help to clean up after having computed everything """
  import os
  for i in os.listdir ( datadir ): 
    try:
      os.unlink ( datadir + "/" + i )
    except Exception,e:
      print "[XSecComputer] error, cannot unlink %s/%s: %s" % ( datadir, i, e )
  try:
    os.rmdir ( datadir )
  except Exception,e:
    print "[XSecComputer] error, cannot rmdir %s: %s" % ( datadir, e )
