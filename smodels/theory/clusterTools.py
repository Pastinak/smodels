"""
.. module:: theory.clusterTools
   :synopsis: Module holding the ElementCluster class and cluster methods used to combine similar elements according
      to the analysis.
        
.. moduleauthor:: Andre Lessa <lessa.a.p@gmail.com>
        
"""

from smodels.theory import crossSection
from smodels.theory.auxiliaryFunctions import massAvg, massPosition, distance
from smodels.tools.physicsUnits import fb
import logging

logger = logging.getLogger(__name__)


class ElementCluster(object):
    """
    An instance of this class represents a cluster.    
    This class is used to store the relevant information about a cluster of
    elements and to manipulate this information.
    
    :ivar elements: list of elements in the cluster (Element objects)    
    """
    def __init__(self):
        self.elements = []

    def __iter__(self):
        return iter(self.elements)

    def __getitem__(self, iel):
        return self.elements[iel]

    def getTotalXSec(self):
        """
        Return the sum over the cross-sections of all elements belonging to
        the cluster.
        
        :returns: sum of weights of all the elements in the cluster (XSectionList object)
        """
        totxsec = crossSection.XSectionList()
        for el in self.elements:
            totxsec.combineWith(el.weight)
        return totxsec

    def getAvgMass(self):
        """
        Return the average mass of all elements belonging to the cluster.
        If the cluster does not refer to a TxName (i.e. in efficiency map results)
        AND the cluster contains more than one element, returns None.
        
        :returns: average mass array         
        """
        
        if self.txname is None:
            if len(self.elements) > 1: return None
            else: return self.elements[0].getMasses()
        
        massList = [el.getMasses() for el in self.elements]
        weights = [el.weight.getMaxXsec() / fb for el in self.elements]        
        return massAvg(massList,weights=weights)


class IndexCluster(object):
    """
    An instance of this class represents a cluster storing element indices.    
    This auxiliary class is used to store element indices and positions in
    upper limit space. It is only used by the clustering algorithm.
    
    :ivar indices: list of integers mapping the cluster elements to their position in the list
                   (1st element -> index 0, 2nd element -> index 1,...)
    :ivar avgPosition: position in upper limit space for the cluster average mass
    :ivar massMap: dictionary with indices as keys and the corresponding element mass as values
    :ivar positionMap: dictionary with indices as keys and the corresponding element position
                        in upper limit space as values
    :ivar weightMap: dictionary with indices as keys and the corresponding element weight
                     as values
    :ivar analysis: analysis to which the cluster applies (ULanalysis object)
    """
    def __init__(self, massMap=None, posMap=None, wMap=None, indices=set([]), txdata = None):
        self.indices = indices
        self.avgPosition = None
        self.massMap = massMap
        self.positionMap = posMap
        self.weightMap = wMap
        self.txdata = txdata


        if massMap and posMap and wMap and len(self.indices) > 0:
            self.avgPosition = self._getAvgPosition()


    def __eq__(self, other):
        if type(self) != type(other):
            return False
        elif set(self.indices) != set(other.indices):
            return False
        else:
            return True


    def __iter__(self):
        return iter(list(self.indices))


    def __getitem__(self, iel):
        return list(self.indices)[iel]
    
    def copy(self):
        """
        Returns a copy of the index cluster (faster than deepcopy).
        """    
      
        newcluster = IndexCluster()
        newcluster.indices = set(list(self.indices)[:])
        newcluster.avgPosition = self.avgPosition
        if type(self.positionMap) == type(dict()):
            newcluster.positionMap = dict(self.positionMap.items())
        else: newcluster.positionMap = None
        if type(self.massMap) == type(dict()):
            newcluster.massMap = dict(self.massMap.items())
        else: newcluster.massMap = None
        if type(self.weightMap) == type(dict()):
            newcluster.weightMap = dict(self.weightMap.items())
        else: newcluster.weightMap = None
        newcluster.analysis = self.analysis
      
        return newcluster


    def add(self, iels):
        """
        Add an index or a list of indices to the list of indices and update
        the avgPosition value.
        
        """
        if type(iels) == type(int()):
            ilist = [iels]
        else:
            ilist = iels

        indices = list(self.indices).extend(ilist)
        self.indices = set(indices)
        self.avgPosition = self._getAvgPosition()


    def remove(self, iels):
        """
        Remove an index or a list of indices to the list of indices and
        update the avgPosition value.
        
        """
        if type(iels) == type(int()):
            ilist = [iels]
        else:
            ilist = iels

        indices = list(self.indices)
        for iel in ilist:
            indices.remove(iel)
        self.indices = set(indices)
        self.avgPosition = self._getAvgPosition()


    def _getAvgPosition(self):
        """
        Return the average position in upper limit space for all indices
        belonging to the cluster.
        
        """
        if len(list(self.indices)) == 1:
            return self.positionMap[self[0]]
        masses = [self.massMap[iel] for iel in self]
        weights = [self.weightMap[iel] for iel in self]
        clusterMass = massAvg(masses,weights=weights)
        avgPos = self.txdata.getValueFor(clusterMass)/fb
        return avgPos.asNumber()


    def _getDistanceTo(self, obj):
        """
        Return the maximum distance between any elements belonging to the
        cluster and the object obj.
        
        obj can be a position in upper limit space or an element index.
        
        """
        dmax = 0.
        if type(obj) == type(int()) and obj >= 0:
            pos = self.positionMap[obj]
        elif type(obj) == type(fb):
            pos = obj
        else:
            logger.error("Unknown object type (must be an element index or "
                         "position)")
            import sys
            sys.exit()

        for jel in self:
            dmax = max(dmax, distance(pos, self.positionMap[jel]))
        return dmax


    def _getMaxInternalDist(self):
        """
        Return the maximum distance between any pair of elements belonging
        to the cluster as well as the cluster center and any element.
        
        """
        dmax = 0.
        if self.avgPosition == None:
            self.avgPosition = self._getAvgPosition()
        for iel in self:
            dmax = max(dmax, distance(self.positionMap[iel], self.avgPosition))
            dmax = max(dmax, self._getDistanceTo(iel))
        return dmax


def groupAll(elements):
    """
    Create a single cluster containing all the elements.
    
    """
    cluster = ElementCluster()
    cluster.elements = elements
    return cluster


def clusterElements(elements, txdata, maxDist):
    """
    Cluster the original elements according to their mass distance.
    
    :parameter elements: list of elements (Element objects)
    :parameter txdata: TxNameData object to be used for computing distances in UL space
    
    :returns: list of clusters (ElementCluster objects)    
    """
    if len(elements) == 0:  return []
    # ElementCluster elements by their mass:
    clusters = _doCluster(elements, txdata, maxDist)
    return clusters


def _doCluster(elements, txdata, maxDist):
    """
    Cluster algorithm to cluster elements.
    
    :parameter elements: list of all elements to be clustered
    :parameter txdata: TxNameData object to be used for computing distances in UL space
    :parameter maxDist: maximum mass distance for clustering two elements
    
    :returns: a list of ElementCluster objects containing the elements
    belonging to the cluster    
    """
    # First build the element:mass, element:position in UL space
    # and element:maxWeight (in fb) dictionaries
    #(Combine elements with identical masses)
    massMap = {}
    posMap = {}
    weightMap = {}
    for iel, el in enumerate(elements):
        if not el.getMasses() in massMap.values():
            massMap[iel] = el.getMasses()
            posMap[iel] = massPosition(massMap[iel], txdata)
            weightMap[iel] = el.weight.getMaxXsec() / fb
        else:
            j = massMap.keys()[massMap.values().index(el.getMasses())] 
            weightMap[j] += el.weight.getMaxXsec() / fb

    # Start with maximal clusters
    clusterList = []
    for iel in posMap:
        indices = [iel]
        for jel in posMap:            
            if distance(posMap[iel], posMap[jel]) <= maxDist:
                indices.append(jel)        
        indexCluster = IndexCluster(massMap, posMap, weightMap, set(indices),txdata)
        clusterList.append(indexCluster)

    #Split the maximal clusters until all elements inside each cluster are
    #less than maxDist apart from each other and the cluster average position
    #is less than maxDist apart from all elements
    finalClusters = []
    newClusters = True
    while newClusters:
        newClusters = []
        for indexCluster in clusterList:
            # cluster is good
            if indexCluster._getMaxInternalDist() < maxDist:
                if not indexCluster in finalClusters:
                    finalClusters.append(indexCluster)
                continue
            # Distance to cluster center (average)
            distAvg = indexCluster._getDistanceTo(indexCluster.avgPosition)
            #Loop over cluster elements and if element distance or cluster
            #average distance falls outside the cluster, remove element
            for iel in indexCluster:
                dist = indexCluster._getDistanceTo(iel)
                if max(dist, distAvg) > maxDist:
                    newcluster = indexCluster.copy()
                    newcluster.remove(iel)
                    if not newcluster in newClusters:
                        newClusters.append(newcluster)

        clusterList = newClusters
        # Check for oversized list of indexCluster (too time consuming)
        if len(clusterList) > 100:
            logger.warning("ElementCluster failed, using unclustered masses")
            finalClusters = []
            clusterList = []

    # finalClusters = finalClusters + clusterList
    # Add clusters of individual masses (just to be safe)
    for iel in massMap:
        finalClusters.append(IndexCluster(massMap, posMap, weightMap,
                                           set([iel])))

    # Clean up clusters (remove redundant clusters)
    for ic, clusterA in enumerate(finalClusters):
        if clusterA is None:
            continue
        for jc, clusterB in enumerate(finalClusters):
            if clusterB is None:
                continue
            if ic != jc and clusterB.indices.issubset(clusterA.indices):
                finalClusters[jc] = None
    while finalClusters.count(None) > 0:
        finalClusters.remove(None)

    # Transform index clusters to element clusters:
    clusterList = []
    for indexCluster in finalClusters:
        cluster = ElementCluster()
        masses = [massMap[iel] for iel in indexCluster]
        for el in elements:
            if el.getMasses() in masses:
                cluster.elements.append(el)
        clusterList.append(cluster)

    return clusterList
