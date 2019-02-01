#!/usr/bin/env python3

import glob
import subprocess
import os

f=open("default.smodels")
lines=f.readlines()
f.close()

copies = []
for line in lines:
    if not "CMS" in line and not "ATLAS" in line:
        continue
    line=line.strip()
    p = line.find(" " )
    line = line[:p]
    copies.append ( line )

cmd = "rm -rf ../smodels-database-small ; mkdir -p ../smodels-database-small/8TeV/CMS ; mkdir -p ../smodels-database-small/8TeV/ATLAS ; mkdir -p ../smodels-database-small/13TeV/CMS ; mkdir -p ../smodels-database-small/13TeV/ATLAS ; cp ../smodels-database/version ../smodels-database-small "
subprocess.getoutput ( cmd )
dirs = glob.glob ( "../smodels-database/*/*/*" )

for Dir in dirs:
    dirname = os.path.dirname ( Dir )
    basename = os.path.basename ( Dir )
    if not basename in copies:
        continue
    newdir = dirname.replace("smodels-database","smodels-database-small" )
    cmd = "cp -r %s %s" % ( Dir, newdir )
    print ( "copying", cmd )
    a=subprocess.getoutput ( cmd )
    print ( a )
