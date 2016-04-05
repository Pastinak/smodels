"""
.. module:: theory.branch
   :synopsis: Module holding the branch class, its methods and related functions.
        
.. moduleauthor:: Andre Lessa <lessa.a.p@gmail.com>
        
"""

from smodels.tools.physicsUnits import fb
from smodels.theory.vertex import createVertexFromStr, Vertex
from smodels.theory.particle import Particle
from smodels.theory.auxiliaryFunctions import stringToList
import logging
from smodels.theory.exceptions import SModelSTheoryError as SModelSError

logger = logging.getLogger(__name__)


class Branch(object):
    """
    An instance of this class represents a branch and it holds a list of vertices (Vertex objects).    
    
    
    :ivar vertexList: list of vertices
    :ivar maxWeight: weight of the branch (XSection object)
    """
    
    def __init__(self, vertices = []):
        """
        Initializes the branch. 
        
        :parameter vertices: list of vertices
        """
        self.vertices = vertices
        self.maxWeight = None


    def __str__(self):
        """
        Create the branch bracket notation string, e.g. [[e+],[jet]].
        
        :returns: string representation of the branch (in bracket notation)    
        """
        
        
        st = str([str(v) for v in self.vertices[1:]])
        st = st.replace("'", "").replace(" ", "")
        return st
    
    
    def __len__(self):
        """
        Defines the branch length (equal to its number of vertices)
        :return: number of vertices in the branch
        """
        
        return len(self.vertices)

    def __cmp__(self,other):
        """
        Compares the branch with other.        
        The comparison is made based on the number of vertices, then on the size of each vertex
        (number of particles in the vertex, then particle masses, see vertex.__cmp__)
        OBS: The particles inside each vertex MUST BE sorted (see vertex.sortParticles())         
        :param other:  branch to be compared (Branch object)
        :return: -1 if self < other, 0 if self == other, +1, if self > other.
        """  
        
        if not isinstance(other,Branch):
            return +1      
        
        if len(self) != len(other):
            comp = len(self) >  len(other)
            if comp: return 1
            else: return -1
        elif self.vertices != other.vertices:
            comp = self.vertices > other.vertices
            if comp: return 1
            else: return -1
        else:
            return 0  #Branches are equal

    def describe(self):
        """
        Extended string representation.
        :return: string represantion in the format 
                    inParticle --> oddParticle + [evenParticles] /
                    inParticle --> oddParticle + [evenParticles] / ...
        """
        
        strR = ""
        for v in self.vertices:
            strR += v.describe() +"/" 
        
        return strR[:-1]

    def copy(self):
        """
        Generate an independent copy of self.        
        Faster than deepcopy.
        
        :returns: Branch object
        """
        newbranch = Branch(vertices = [v.copy() for v in self.vertices])
        if not self.maxWeight is None:
            newbranch.maxWeight = self.maxWeight.copy()
        return newbranch

    def sortVertices(self):
        """
        Sorts the particles in each vertex
        """
        
        for v in self.vertices:
            v.sortParticles()
            
    def getOddMasses(self):
        """
        Get the array of odd particle masses in the branch.
        :returns: list of masses (mass array)            
        """
        massarray = []
        for v in self.vertices:
            massarray += [p.mass for p in v.outOdd]
        return massarray
    
    
    def combinePIDs(self,other):
        """
        Combine the PIDs of both branches (_pid property of the odd particles).
        If the PIDs already appear in self,  do not add them to the list.
        
        :parameter other: branch (Branch Object) 
        """
        
        if len(self.vertices)!= len(other.vertices):
            logger.warning("Can not combine PIDs. Branches have distinct number of vertices.")
            return

        for iv,v in enumerate(self.vertices):
            v.combinePIDs(other.vertices[iv])
            
    def getOddPIDs(self):
        """
        Return the (nested) list of PIDs for the outgoing odd particles.
        If the branch combines distinct PIDs, the list may be nested.
        :return: List of PIDs 
                (e.g. [pidA,pidB,pidC] for a simple element)
                (e.g. [pidA,[pidB1,pidB2],pidC] for a combined branch) 
        """
        
        pids = [v.getOddPIDs() for v in self.vertices]
        
        return pids            

    def _addVertex(self, newVertex):
        """
        Generate a new branch adding the new vertex to the original branch.
        The PID of incoming particle in the new Vertex must match one of the PIDs of outgoing
        particles in the last vertex of the original branch.
        
        :parameter newVertex: Vertex object. Contains both incoming and outgoing particles.  
        :return: extended branch (Branch object). False if there was an error.
        """
        
        if not newVertex.inParticle._pid in [p._pid for p in self.vertices[-1].outParticles]:
            logger.error("New vertex incoming particle does not match"
                           + " any of the last vertex outgoing particles")
            raise SModelSError
        
        newBranch = self.copy()
        newV = newVertex.copy()
        newBranch.vertices.append(newV)
        if not self.maxWeight is None and hasattr(newVertex,'br'):
            newBranch.maxWeight = self.maxWeight*newVertex.br
                

        return newBranch

    def decay(self, vertexDecayDict):
        """
        Generate a list of all new branches generated by the 1-step cascade
        decay of the current branch daughter (outgoing particles in its last vertex).
        OBS: There must be a single (or none) unstable particle in the last vertex. 
        
        :parameter vertexDecayDict: dictionary with the decay vertices 
                                 for all odd particles. 
                                 Keys are PIDs and values are a list of vertices.

        :returns: list of extended branches (Branch objects). Empty list if daughter is stable.
        """

        nUnstable = 0
        newVertices = None
        for p in self.vertices[-1].outParticles:
            if p._pid in vertexDecayDict:
                nUnstable += 1
                newVertices = vertexDecayDict[p._pid]

        if nUnstable > 1:
            logger.error("Can not decay vertex with multiple unstable outgoing particles")
            return False
        elif nUnstable == 0:
            return []
        
        newBranches = [self._addVertex(newVertex) for newVertex in newVertices]
        return newBranches

    def massCompress(self,minmassgap):
        """
        Perform mass compression.
        
        :parameter minmassgap: value (in GeV) of the maximum 
                               mass difference for compression
                               (if mass difference < minmassgap -> perform mass compression)
        :returns: compressed copy of the branch, if two masses in this
                  element are degenerate; None, if compression is not possible;        
        """
        
        newBranch = self.copy()
        newBranch.vertices = [newBranch.vertices[0]]        
        #Add vertices to new branch
        for v in self.vertices[1:]:            
            if len(newBranch.vertices[-1].outOdd) != 1 or len(v.outOdd) != 1:
                logger.warning("Compression with multiple (or none) odd"
                               +" outgoing particles in a vertex is not implemented.")
                return None
            if newBranch.vertices[-1].outOdd[0] != v.inParticle:
                logger.warning("Incoming and out going particles do not match."
                               +" Compression will not be applied.")
                return None                            
            massDiff = v.inParticle.mass - v.outOdd[0].mass
            if massDiff.asNumber() < 0.:
                logger.error("Odd masses in vertex dot not decrease monotonically")
                raise SModelSError                
            elif massDiff < minmassgap:
                #Vertex to be added is ~ degenerate
                #Replace outgoing odd particle from previous vertex by the new one                
                newBranch.vertices[-1].outOdd[0] = v.outOdd[0]
            else:
                newBranch.vertices.append(v.copy())


        if len(newBranch) == len(self):
            return None  #Branch was not compressed
        
        return newBranch
    
    def invisibleCompress(self):
        """
        Perform invisible compression.
        
        :returns: compressed copy of the branch, if the branch ends with invisible
                  particles (zero eCharge and zero qColor);
                  None, if compression is not possible
        """
        
        newBranch = self.copy()        
        for iv in range(-1,-len(self.vertices),-1):
            v = self.vertices[iv]            
            qTotal = 0
            colorTotal = 0
            for p in v.outParticles:
                if hasattr(p, 'eCharge'):
                    qTotal += abs(p.eCharge)
                if hasattr(p, 'qColor'):
                    colorTotal += abs(p.qColor)
            #If the total charge of the final particles of the
            #last cascade decay are zero
            if qTotal + colorTotal == 0:
                #Remove last vertex
                newBranch.vertices.pop(-1)
                #Check if effective charge of last vertex is zero:
                if not (v.inParticle.eCharge == 0 and  v.inParticle.qColor == 0):
                    logger.error("Charge does not seem to be conserved at:\n %s" 
                                 %v.stringRep())
                    raise SModelSError         
            else:
                break #If not, stop here
        
        if len(newBranch) == len(self):  #Branch could not be compressed
            return None
        else:
            return newBranch


def createBranchFromStr(branchStr):
    """
    Creates a branch from a string in bracket notation (e.g. [[e+],[jet]]).
    The cascade decay is assumed to follow a proper topology (e.g. odd_A -> odd_B + e+ -> odd_C + jet).  
    Odd-particles are created as empty Particle objects and Even-particles are
    created using the particles pre-defined (by the user) which match the corresponding
    particle label.
    The last odd particle in the cascade (e.g. odd_C) is assumed to be neutral
    (missing ET signature).
    :branchStr: string (e.g. [[e+],[jet]])
    :return: Branch object
    """
    
    #Start with a simple vertex (only with one outgoing mother)
    vertices = [Vertex(outParticles=[Particle(zParity=-1, _name = 'Mother')])]
    for vertex in stringToList(branchStr):
        vertices.append(createVertexFromStr(str(vertex))) 
    
    vertices[-1].outOdd[0].eCharge = 0
    vertices[-1].outOdd[0].qCharge = 0  #Assumes the last odd particle is neutral
    vertices[-1].outOdd[0]._name = "Daughter"
    return Branch(vertices=vertices)

def decayBranches(branchList, vertexDecayDict, sigcut=0. *fb):
    """
    Decay all branches from branchList until all unstable states have decayed.
    
    :parameter branchList: list of Branch() objects containing the first vertex (produced mother and its decay)
    :parameter vertexDecayDict: dictionary with the decay vertices 
                                 for all odd particles. Keys are PIDs and values are a list of vertices.
    :parameter sigcut: minimum sigma*BR to be generated, by default sigcut = 0.
                   (all branches are kept)
    :returns: list of branches (Branch objects)    
    """

    finalBranchList = []
    while branchList:
        # Store branches after adding one step cascade decay
        newBranchList = []
        for inbranch in branchList:
            if sigcut.asNumber() > 0. and inbranch.maxWeight < sigcut:
                # Remove the branches above sigcut and with length > topmax
                continue
            # Add all possible decays of the last vertex to the original branch
            newBranches = inbranch.decay(vertexDecayDict)
            if newBranches:
                # New branches were generated, add them for next iteration
                newBranchList.extend(newBranches)
            else:
                # All particles have already decayed, store final branch
                finalBranchList.append(inbranch)
        # Use new branches (if any) for next iteration step
        branchList = newBranchList
        
    #Sort list by initial branch PID:
    finalBranchList = sorted(finalBranchList, key=lambda branch: branch.vertices[0].outOdd[0]._pid)
    return finalBranchList
