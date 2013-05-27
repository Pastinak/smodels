#!/usr/bin/python

""" Systematically run all scripts and check if we get an error """

import os, sys
from TestTools import ok

Dir="../bin/"

scripts=os.listdir ( Dir )

print "Start to systematically check all scripts:\n"

for script in scripts:
  if script[-3:]!=".py": continue
  if script=="run_all.py": continue
  if script=="set_path.py": continue
  print "%s: " % ( script ),
  cmd= "python " + Dir + script + " > /dev/null"
  ret=os.system ( cmd )
  print ok ( 0, ret )

print "\nFinally check SMSmain.py: ",
os.chdir("..")
cmd= "python SMSmain.py > /tmp/compare"
ret=os.system ( cmd )
print ok ( 0, ret )

import commands
out=commands.getoutput("diff /tmp/compare SMSmain.log")
print "Diff of the logs: %s" % ok ( "", out )
