"""
.. module:: element
   :synopsis: Module holding the Element class and its methods.
    
.. moduleauthor:: Andre Lessa <lessa.a.p@gmail.com>
    
"""

from smodels.theory.branch import Branch
from smodels.theory import crossSection
from smodels.tools.smodelsLogging import logger
from smodels.theory.exceptions import SModelSTheoryError as SModelSError

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
    def __init__(self, info=None):
        """
        Initializes the element. If info is defined, tries to generate
        the element using it.
        
        :parameter info: string describing the element in bracket notation
                         (e.g. [[[e+],[jet]],[[e-],[jet]]])
        """
        self.branches = []
        self.weight = crossSection.XSectionList()
        self.motherElements = []
        self.elID = 0
        self.covered = False
        self.tested = False
                
        if isinstance(info,str):
            self.fromString(info)
        elif isinstance(info,list):
            if all([isinstance(b,str) for b in info]):
                self.branches = info
        elif info:
            logger.error("Invalid argument type: %s" %type(info))
            raise SModelSError()
            
        self.sortBranches()
            
            
    def fromString(self,elementStr):
        """
        Creates an element from the the element string
        
        :param elementStr: string representing an element in bracket notation
        """
        
        branchStrings = elementStr[elementStr.find('['):elementStr.rfind(']')].split(',')
        self.branchs = [Branch(bStr) for bStr in branchStrings]
        
    
    def __cmp__(self,other):
        """
        Compares the element with other.        
        The comparison is made based on branches.
        OBS: The elements and the branches must be sorted! 
        :param other:  element to be compared (Element object)
        :return: -1 if self < other, 0 if self == other, +1, if self > other.
        """
        
        #Compare branches:
        if self.branches != other.branches:            
            comp = self.branches > other.branches
            if comp: return 1
            else: return -1
        else:
            return 0     

    def __eq__(self,other):
        return self.__cmp__(other)==0

    def __lt__(self,other):
        return self.__cmp__(other)<0

    def __hash__(self):
        return object.__hash__(self)


    def __str__(self):
        """
        Create the element bracket notation string, e.g. [[[jet,MET]],[[jet,MET]].
        
        :returns: string representation of the element (in bracket notation)    
        """
        particleString = str(self.getFinalStates()).replace(" ", "").\
                replace("'", "")
        return particleString
    
    def sortBranches(self):
        """
        Sort branches. The smallest branch is the first one.
        See the Branch object for definition of branch size and comparison
        """
        
        #First make sure each branch is individually sorted 
        #(particles in each vertex are sorted)
        for br in self.branches:
            br.sortVertices()
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

    def switchBranches(self):
        """
        Switch branches, if the element contains a pair of them.
        
        :returns: element with switched branches (Element object)                
        """
        
        newEl = self.copy()
        if len(self.branches) == 2:
            newEl.branches = [newEl.branches[1], newEl.branches[0]]
        return newEl

    def getParticles(self):
        """
        Get the array of all particles appearing in the element.
        
        :returns: nested list of particle objects            
        """
        
        finalStates = []
        for branch in self.branches:
            finalStates.append(branch.getParticles())
        return finalStates



    def getFinalStates(self):
        """
        Get the array of particles appearing as a final state in the element.
        
        :returns: nested list of particle objects            
        """
        
        finalStates = []
        for branch in self.branches:
            finalStates.append(branch.getFinalStates())
        return finalStates
    
    def getOddStates(self):
        """
        Get the array of odd particle objects appearing in the element.
        
        :returns: nested list of particle objects                
        """
        
        oddStates = []
        for branch in self.branches:
            oddStates.append(branch.getOddStates())
        return oddStates

    def getEvenStates(self):
        """
        Get the array of even particle objects appearing in the element.
        
        :returns: nested list of particle objects                
        """
        
        evenStates = []
        for branch in self.branches:
            evenStates.append(branch.getEvenStates())
        return evenStates


    def getOddMasses(self):
        """
        Get the array of masses for the odd particles appearing in the element.    
        
        :returns: nested list of masses (mass array)            
        """
        massarray = []
        for branch in self.branches:
            massarray.append(branch.getOddMasses())
        return massarray

    def getOddPIDs(self):
        """
        Get the PIDs for the odd particles appearing in the element.
        If the element particles receives contributions from distinct PIDs,
        the result may be a nested list.
        
        :returns: nested list of PDG ids
        """
        
        pids = []
        oddStates = self.getOddStates()
        for oddParticle in oddStates:
            pids.append(oddParticle.PIDs)
        
        return pids

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
        
        if not doCompress and not doInvisible:
            return []
        
        added = True
        newElements = [self]
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
                    if newel and not newel.hasTopInList(newElements):
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
        
        masses = self.getMasses()
        massDiffs = []
        #Compute mass differences in each branch
        for massbr in masses:
            massDiffs.append([massbr[i]-massbr[i+1] for i in range(len(massbr)-1)])
        #Compute list of vertices to be compressed in each branch            
        compVertices = []
        for ibr,massbr in enumerate(massDiffs):
            compVertices.append([])
            for iv,massD in enumerate(massbr):            
                if massD < minmassgap: compVertices[ibr].append(iv)
        if not sum(compVertices,[]): return None #Nothing to be compressed
        else:
            newelement = self.copy()
            newelement.motherElements = [ ("mass", self) ]
            for ibr,compbr in enumerate(compVertices):
                if compbr:            
                    new_branch = newelement.branches[ibr]
                    ncomp = 0
                    for iv in compbr:
                        new_branch.masses.pop(iv-ncomp)
                        new_branch.particles.pop(iv-ncomp)
                        ncomp +=1
                    new_branch.setInfo() 

        newelement.sortBranches()
        return newelement
    

    def hasTopInList(self, elementList):
        """
        Check if the element topology matches any of the topologies in the
        element list.
        
        :parameter elementList: list of elements (Element objects)
        :returns: True, if element topology has a match in the list, False otherwise.        
        """
        if type(elementList) != type([]) or len(elementList) == 0:
            return False
        for element in elementList:
            if type(element) != type(self):
                continue
            info1 = self.getEinfo()
            info2 = element.getEinfo()
            info2B = element.switchBranches().getEinfo()
            if info1 == info2 or info1 == info2B:
                return True
        return False


    def invisibleCompress(self):
        """
        Perform invisible compression.
        
        :returns: compressed copy of the element, if element ends with invisible
                  particles; None, if compression is not possible
        """
        newelement = self.copy()
        newelement.motherElements = [ ("invisible", self) ]

        # Loop over branches
        for ib, branch in enumerate(self.branches):
            particles = branch.particles
            if not branch.particles:
                continue # Nothing to be compressed
            #Go over the branch starting at the end and remove invisible vertices: 
            for ivertex in reversed(range(len(particles))):
                if particles[ivertex].count('nu') == len(particles[ivertex]):
                    newelement.branches[ib].masses.pop(ivertex+1)
                    newelement.branches[ib].particles.pop(ivertex)
                else:
                    break
            newelement.branches[ib].setInfo()

        newelement.sortBranches()
        if newelement == self:
            return None
        else:            
            return newelement


    def combineMotherElements ( self, el2 ):
        """
        Combine mother elements from self and el2 into self
        
        :parameter el2: element (Element Object)  
        """
        
        self.motherElements += el2.motherElements


    def combinePIDs(self,el2):
        """
        Combine the PIDs of both elements. If the PIDs already appear in self,
        do not add them to the list.
        
        :parameter el2: element (Element Object) 
        """
           
        elPIDs = self.getPIDs()
        newelPIDs = el2.getPIDs()
        for pidlist in newelPIDs:                    
            if not pidlist in elPIDs:
                self.branches[0].PIDs.append(pidlist[0])
                self.branches[1].PIDs.append(pidlist[1])
