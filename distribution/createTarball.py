#!/usr/bin/env python

"""
.. module:: createTarball
   :synopsis: Script that is meant to create the distribution tarball

.. moduleauthor:: Wolfgang Waltenberger <wolfgang.waltenberger@gmail.com>
   
"""

import sys
import commands
import os
import time

RED = "\033[31;11m"
GREEN = "\033[32;11m"
RESET = "\033[7;0m"

def comment( text ):
    print "%s[%s] %s %s" % ( RED, time.asctime(),text,RESET )
    f=open("create.log","a")
    f.write (  "[%s] %s\n" % ( time.asctime(),text ) )
    f.close()

def run ( cmd ):
    print "%scmd: %s%s" % (GREEN,cmd,RESET)
    f=open("create.log","a")
    f.write ( "cmd: %s\n" % (cmd) )
    o=commands.getoutput ( cmd )
    print o
    f.write ( o + "\n" )
    f.close()

def getVersion():
    """
    Obtain the smodels version """
    sys.path.append("../")
    from smodels import installation
    return installation.version()

version = getVersion()
dirname = "smodels-v%s" % version

def rmlog():
    """ clear the log file """
    cmd="rm -f create.log"
    commands.getoutput ( cmd )

def mkdir():
    """
    Create a temporary directory for creating the tarball.
    """
    comment ("Creating temporary directory %s" %  dirname )
    run ("mkdir -p %s" % dirname)

def rmdir():
    """
    Remove the temporary directory.
    """
    if os.path.exists(dirname):
        comment ( "Removing temporary directory %s" % dirname )
        run ("rm -rf %s" % dirname)


def cp():
    """
    Copy files to temporary directory.
    """
    comment ( "Copying the files to %s" % dirname )
    for i in os.listdir("../"):
        if i not in [".git", ".gitignore", "distribution", "test"]:
            run ("cp -r ../%s %s/" % (i, dirname))

def clone():
    """
    Git clone smodels itself into dirname, then remove .git, .gitignore, distribution, and test.
    """
    comment ( "Git-cloning smodels into %s (this might take a while)" % dirname )
    run ("git clone git@smodels.hephy.at:smodels %s" % (dirname) )
    for i in os.listdir( dirname ):
        if i in [".git", ".gitignore", "distribution", "test"]:
            run ( "rm -rf %s/%s" % (dirname,i) )

def rmpyc ():
    """
    Remove .pyc files.
    """
    comment ( "Removing all pyc files ... " )
    run ("cd %s; rm -f *.pyc */*.pyc */*/*.pyc" % dirname)


def makeClean ():
    """
    Execute 'make clean' in host directory.
    """
    comment ( "Make clean ...." )
    run ("cd ../lib/ ; make clean")

def fetchDatabase():
    """
    Execute 'git clone' to retrieve the database.
    """
    comment ( "git clone the database (this might take a while)" )
    cmd = "cd %s; git clone -b v%s git@smodels.hephy.at:smodels-database ;" \
        " rm -rf smodels-database/.git smodels-database/.gitignore " % \
            (dirname, version)
    run ( cmd )

def createTarball():
    """
    Create the tarball.
    """
    comment ( "Create tarball smodels-v%s.tar.gz" % version )
    run ("tar czvf smodels-v%s.tar.gz %s" % (version, dirname))

def rmExtraFiles():
    """
    Remove additional files.
    """
    comment ( "Remove a few unneeded files" )
    extras = [ "inputFiles/slha/nobdecay.slha" ]
    for i in extras:
        cmd = "rm -rf %s/%s" % ( dirname, i )
        run ( cmd )

def convertRecipes():
    """
    Compile recipes from .ipynb to .py and .html.
    """
    comment ( "Converting the recipes" )
    cmd = "cd %s/docs/manual/source/recipes/; make convert remove_ipynbs" % dirname
    run (cmd)

def makeDocumentation():
    """
    create the documentation via sphinx """
    comment ( "Creating the documentation" )
    cmd = "cd %s/docs/manual/; make html; rm -r make.bat Makefile source " % dirname
    run (cmd)
    cmd = "cd %s/docs/documentation/; make html; rm -r make.bat  Makefile source update" % dirname
    run (cmd)

def explode ():
    """
    Explode the tarball.
    """
    comment ( "Explode the tarball ..." )
    cmd = "tar xzvf smodels-v%s.tar.gz" % version
    run (cmd)

def make ():
    """
    Execute 'make' in dirname/lib.
    """
    comment ( "Now run make in dirname/lib ..." )
    cmd = "cd %s/lib; make" % dirname
    run (cmd)

def runExample ():
    """
    Execute Example.py.
    """
    comment ( "Now run Example.py ..." )
    cmd = "cd %s/; ./Example.py" % dirname
    run (cmd)

def test ():
    """
    Test the tarball, explode it, execute 'make', and 'runSModelS.py'.
    """
    comment ( "--------------------------" )
    comment ( "    Test the setup ...    " )
    comment ( "--------------------------" )
    rmdir ()
    explode ()
    make ()
    runExample()

def testDocumentation():
    """ Test the documentation """
    comment ( "Test the documentation" )
    cmd="ls %s/docs/manual.html" % dirname 
    run (cmd)

def create():
    """
    Create a tarball for distribution.
    """
    rmlog() ## first remove the log file
    comment ( "Creating tarball for distribution, version %s" % version )
    # makeClean()
    rmdir()
    mkdir() ## .. then create the temp dir
    ## cp()
    clone() ## ... clone smodels into it ...
    rmExtraFiles() ## ... remove unneeded files ...
    fetchDatabase() 
    makeDocumentation()
    convertRecipes()
    rmpyc() ## ...  remove the pyc files created by makeDocumentation ...
    createTarball() ## here we go! create!
    test ()
    # rmdir(dirname)
    testDocumentation()


if __name__ == "__main__":
    create()
