"""
.. module:: theory.element
   :synopsis: Module holding the Element class and its methods.
    
.. moduleauthor:: Andre Lessa <lessa.a.p@gmail.com>
    
"""

from smodels.theory import crossSection
from smodels.theory.auxiliaryFunctions import stringToList
from smodels.theory.branch import createBranchFromStr
import logging
import itertools
logger = logging.getLogger(__name__)


class Element(object):
    """
    An instance of this class represents an element.    
    This class possesses a pair of branches and the element weight
    (cross-section * BR).
    
    :ivar branches: list of branches (Branch objects)
    :ivar weight: element weight (cross-section * BR)
    :ivar motherElements: only for elements generated from a parent element
                          by mass compression, invisible compression,etc.
                          Holds a pair of (whence, mother element), where
                          whence describes what process generated the element    
    """
    def __init__(self, branches=[]):
        """
        Initializes the element. If info is defined, tries to generate
        the element using it.
        
        :parameter branches: List of branch objects
        """
        self.branches = branches
        self.weight = crossSection.XSectionList()
        self.motherElements = []
        self.elID = 0
        self.covered = 0 # how many analyses cover this element?
        
        self.sortBranches()

    def __cmp__(self,other):
        """
        Compares the element with other.        
        The comparison is made based on branches irrespect of branch ordering.
        OBS: The elements and the branches must be sorted in order for the > (<)
        comparison to make sense. 
        :param other:  element to be compared (Element object)
        :return: -1 if self < other, 0 if self == other, +1, if self > other.
        """
        
        if not isinstance(other,Element):
            return +1
        
        #First compare number of branches:        
        if len(self.branches) != len(other.branches):            
            comp = len(self.branches) > len(other.branches)
            if comp: return 1
            else: return -1
        #If both have the same number of branches compare
        #all possible branch orderings (for 2 branches there are only 2 options)
        branchLists = [list(br) for br in itertools.permutations(self.branches)]
        match = False
        for branches in branchLists:
            if branches == other.branches:
                match = True
                break
        #There is at one branch ordering which matches: 
        if not match:
            comp = self.branches > other.branches
            if comp: return 1
            else: return -1
        else:
            return 0     


    def __hash__(self):
        return object.__hash__(self)


    def __str__(self):
        """
        Create the element bracket notation string, e.g. [[[jet]],[[jet]].
        
        :returns: string representation of the element (in bracket notation)    
        """
        
        st = str([str(b) for b in self.branches])
        st = st.replace("'", "").replace(" ", "")
        return st
    
    def describe(self):
        """
        Extended string representation.
        :return: string represantion in the format 
                    B0: inParticle --> oddParticle + [evenParticles] / ...
                    B1: inParticle --> oddParticle + [evenParticles] / ...
        """
        
        strR = ""
        for ib,b in enumerate(self.branches):
            strR += "B"+str(ib)+": " + b.describe() +"\n" 
        
        return strR
    
    def getEinfo(self):
        """
        Get element info (list of vertices in the branches and
        number of outgoing particles in each vertex).
        
        :returns: dictionary containing number vertices 
                    and number of outgoing particles in each vertex.
        """
        
        vertnumb = [b.getBinfo()['vertnumb'] for b in self.branches]
        vertparts = [b.getBinfo()['vertparts'] for b in self.branches]
        
        return {"vertnumb" : vertnumb, "vertparts" : vertparts}
    
    def sortBranches(self):
        """
        Sort branches. The smallest branch is the first one.
        See the Branch object for definition of branch size and comparison
        """
        
        #First make sure each branch is individually sorted 
        #(particles in each vertex are sorted)
        for br in self.branches:
            br.sortVertices()  #Sort particles in each vertex
        #Now sort branches
        self.branches = sorted(self.branches)


    def copy(self):
        """
        Create a copy of self.        
        Faster than deepcopy.     
        
        :returns: copy of element (Element object)   
        """
        newel = Element()
        newel.branches = []
        for branch in self.branches:
            newel.branches.append(branch.copy())
        newel.weight = self.weight.copy()
        newel.motherElements = self.motherElements[:]
        newel.elID = self.elID
        return newel

    def getOddMasses(self):
        """
        Get the array of odd particle masses in the element.
        :returns: list of masses (mass array)            
        """
        massarray = []
        for branch in self.branches:
            massarray.append(branch.getOddMasses())
        return massarray
    
    def compressElement(self, doCompress, doInvisible, minmassgap):
        """
        Keep compressing the original element and the derived ones till they
        can be compressed no more.
        
        :parameter doCompress: if True, perform mass compression
        :parameter doInvisible: if True, perform invisible compression
        :parameter minmassgap: value (in GeV) of the maximum 
                               mass difference for compression
                               (if mass difference < minmassgap, perform mass compression)
        :returns: list with the compressed elements (Element objects)        
        """
        added = True
        newElements = [self.copy()]
        # Keep compressing the new topologies generated so far until no new
        # compressions can happen:
        while added:
            added = False
            # Check for mass compressed topologies
            if doCompress:
                for element in newElements:
                    newel = element.massCompress(minmassgap)
                    # Avoids double counting (conservative)
                    if newel and not newel.hasTopInList(newElements):
                        newElements.append(newel)
                        added = True

            # Check for invisible compressed topologies (look for effective
            # LSP, such as LSP + neutrino = LSP')
            if doInvisible:
                for element in newElements:
                    newel = element.invisibleCompress()
                    # Avoids double counting (conservative)
                    if newel and not newel in newElements:
                        newElements.append(newel)
                        added = True

        newElements.pop(0)  # Remove original element
        return newElements

    def massCompress(self, minmassgap):
        """
        Perform mass compression.
        
        :parameter minmassgap: value (in GeV) of the maximum 
                               mass difference for compression
                               (if mass difference < minmassgap -> perform mass compression)
        :returns: compressed copy of the element, if two masses in this
                  element are degenerate; None, if compression is not possible;        
        """
        
        newelement = self.copy()
        compBranches = [br.massCompress(minmassgap) for br in self.branches]
        if compBranches.count(None) == len(compBranches):
            return None #No branch was compressed
        else:
            for ibr,br in enumerate(compBranches):
                if br:
                    newelement.branches[ibr] = br
        newelement.motherElements = [ ("mass", self.copy()) ]

        newelement.sortBranches()
        return newelement


    def invisibleCompress(self):
        """
        Perform invisible compression.
        
        :returns: compressed copy of the element, if element ends with invisible
                  particles; None, if compression is not possible
        """
        
        newelement = self.copy()
        compBranches = [br.invisibleCompress() for br in self.branches]
        if compBranches.count(None) == len(compBranches):
            return None #No branch was compressed
        else:
            for ibr,br in enumerate(compBranches):
                if br:
                    newelement.branches[ibr] = br
        newelement.motherElements = [ ("invisible", self.copy()) ]

        newelement.sortBranches()
        return newelement
        
    def combineWith(self,other):
        """
        Combined the element with other.
        Combine the elements weights, their mothers and PIDs.
        
        :parameter other: element (Element Object)  
        """
        
        if self.getEinfo() != other.getEinfo():
            logger.warning("Element structures do not match and can not be combined.")
            return
        
        self.combineMotherElements(other)
        self.combinePIDs(other)
        self.weight.combineWith(other.weight)


    def combineMotherElements ( self, other ):
        """
        Combine mother elements from self and other into self
        
        :parameter other: element (Element Object)  
        """
        if len(self.motherElements)==0: 
            # no mothers? then you yourself are mother!
            tmp=self.copy()
            self.motherElements.append ( ("combine", tmp) )
        for m in other.motherElements:
            self.motherElements.append ( (m[0], m[1].copy()) )
        if len(other.motherElements)==0: 
            # no mothers? then yo yourself are mother now
            tmp=other.copy()
            self.motherElements.append ( ("combine", tmp) )


    def combinePIDs(self,other):
        """
        Combine the PIDs of both elements (_pid property of the odd particles).
        If the PIDs already appear in self,  do not add them to the list.
        
        :parameter other: element (Element Object) 
        """
        
        if len(self.branches)!= len(other.branches):
            logger.warning("Can not combine PIDs. Elements have distinct number of branches.")
            return

        for ib,br in enumerate(self.branches):
            br.combinePIDs(other.branches[ib])
            
    def getOddPIDs(self):
        """
        Return the (nested) list of PIDs for the outgoing odd particles.
        If the element combines distinct PIDs, the list may be nested.
        :return: List of PIDs 
                (e.g. [ [pidA,pidB,pidC], [pid1, pid2] ] for a simple element)
                (e.g. [ [pidA,[pidB1,pidB2],pidC], [[pid11,pid12], pid2] ] for a combined element) 
        """
        
        pids = [b.getOddPIDs() for b in self.branches]
        
        return pids

def createElementFromStr(branchStr):
    """
    Creates an element from a string in bracket notation (e.g. [[[e+],[jet]], [[mu+,L],[e-]]]).
    Odd-particles are created as empty Particle objects and Even-particles are
    created using the particles pre-defined (by the user) which match the corresponding
    particle label/name.
    The last odd particle in the cascade branches are assumed to be neutral
    (missing ET signature).
    :branchStr: string (e.g. [[[e+],[jet]], [[mu+,L],[e-]]])
    :return: Element object
    """
    
    branches = []
    for br in stringToList(branchStr):
        branches.append(createBranchFromStr(str(br))) 

    return Element(branches=branches)