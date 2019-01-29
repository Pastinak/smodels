"""
.. module:: particle
   :synopsis: Defines the particle class and particle list class, their methods and related functions

.. moduleauthor:: Alicia Wongel <alicia.wongel@gmail.com>
.. moduleauthor:: Andre Lessa <lessa.a.p@gmail.com>
"""

import copy

class Particle(object):
    """
    An instance of this class represents a single particle. 
    The properties are: label, pdg, mass, electric charge, color charge, width 
    """

    def __init__(self, **kwargs):
        """ 
        
        Initializes the particle.
        Possible properties: 
        Z2parity: int, +1 or -1
        label: str, e.g. 'e-'
        pdg: number in pdg
        mass: mass of the particle
        echarge: electric charge as multiples of the unit charge
        colordim: color dimension of the particle 
        spin: spin of the particle
        width: total width
        decays: possible decays in pyslha format e.g. [ 0.5[1000022, -1], 0.5[1000022, -2] ]
                 
        """  

        self._static = False
        for attr,value in kwargs.items():
            if not attr == '_static':
                setattr(self,attr,value)

        self.id = None
        self.setID()
        #Leave the static attribute for last:
        if '_static' in kwargs:
            self._static = kwargs['_static']

    def setID(self):
        """
        Defines the particle ID. If the particle has a comparison matrix,
        the ID will be defined as its dimension and the matrix will be extended.
        Otherwise the ID will be set to None.
        """
        #If a comparison matrix has been defined, use it
        #to set the element id:
        if hasattr(self, 'cmpMatrix'):
            self.id = len(self.cmpMatrix[0]) #Set ID as the next entry in cmpMatrix
            #Add a column and a line to cmpMatrix with None
            for iline,line in enumerate(self.cmpMatrix):
                self.cmpMatrix[iline] = line + [None]
            self.cmpMatrix.append([None for i in range(len(self.cmpMatrix[0])+1)])

    def __cmp__(self,other):
        """
        Compares particle with other.
        The comparison is based on the particle properties.
        If the particles differ they are sorted according to their label.
        If in addition the particles differ, but have the same label, they
        are sorted according to their properties.
        
        :param other:  particle to be compared (Particle object)
        
        :return: -1 if self.label < other.label, 0 if self == other, +1, if self.label > other.label.
        """    
        
        if not isinstance(other,(MultiParticle,Particle)):
            return +1
        if self.id == other.id and not self.id is None:
            return 0

        #Check if particles ID have been defined
        try:
            comp = self.cmpMatrix[self.id][other.id]
            if comp is None:
                comp = self.cmpProperties(other)
                self.cmpMatrix[self.id][other.id] = comp
                self.cmpMatrix[other.id][self.id] = -comp
            return comp
        except (AttributeError,TypeError):
            try:
                comp = other.cmpMatrix[self.id][other.id]
                if comp is None:
                    comp = self.cmpProperties(other)
                    other.cmpMatrix[self.id][other.id] = comp
                    other.cmpMatrix[other.id][self.id] = -comp
                return comp
            except (AttributeError,TypeError):
                pass
        #If everything fails, compare particle properties
        return self.cmpProperties(other)

    def __lt__( self, p2 ):
        return self.__cmp__(p2) == -1

    def __gt__( self, p2 ):
        return self.__cmp__(p2) == 1

    def __eq__( self, p2 ):
        return self.__cmp__(p2) == 0
        
    def __ne__( self, p2 ):
        return self.__cmp__(p2) != 0

    def __str__(self): 
        if hasattr(self, 'label'):
            return self.label
        else: return ''
        
    def __repr__(self):
        return self.__str__()        
    
    def __setattr__(self,attr,value):
        """
        Override setattr method.
        If the _static attribute is True, will not
        change the particle attribute.
        """
          
        if attr == '_static':
            self.__dict__[attr] = value
        elif self._static is False:            
            self.__dict__[attr] = value
     
    def __setstate__(self, state):
        """
        Override setstate method. Required for pickling.
        """

        self._static = False
        self.__dict__.update(state)

    def __add__(self, other):
        """
        Define addition of two Particle objects
        or a Particle object and a MultiParticle object.
        The result is a MultiParticle object containing
        both particles.
        """

        if not isinstance(other,(MultiParticle,Particle)):
            raise TypeError("Can only add particle objects")
        elif isinstance(other,MultiParticle):
            return other.__add__(self)
        elif self.contains(other):
            return self
        elif other.contains(self):
            return other
        else:
            combined = MultiParticle(label = 'multiple', particles= [self,other])
            return combined

    def __radd__(self,other):
        return self.__add__(other)

    def __iadd__(self,other):
        return self.__add__(other)


    def describe(self):
        return str(self.__dict__)

    def eqProperties(self,other, 
                     properties = ['Z2parity','spin','colordim','eCharge','mass','totalwidth']):
        """
        Check if particle has the same properties (default is spin, colordim and eCharge)
        as other. Only compares the attributes which have been defined in both objects.
        
        :param other: a Particle or MultiParticle object
        :param properties: list with properties to be compared. Default is spin, colordim and eCharge
        
        :return: True if all properties are the same, False otherwise.
        """
        
        if self.cmpProperties(other, properties=properties) == 0:
            return True
        else:
            return False
            
    def cmpProperties(self,other, 
                      properties = ['Z2parity','spin','colordim','eCharge','mass','totalwidth']):
        """
        Compare properties (default is spin, colordim and eCharge).
        Return 0 if properties are equal, -1 if self < other and 1 if self > other.
        Only compares the attributes which have been defined in both objects.
        The comparison is made in hierarchical order, following the order
        defined by the properties list.
        
        :param other: a Particle or MultiParticle object
        :param properties: list with properties to be compared. Default is spin, colordim and eCharge
        
        :return: 0 if properties are equal, -1 if self < other and 1 if self > other.
        """

        if isinstance(other,(MultiParticle)):
            return -1*other.cmpProperties(self,properties=properties)
        
        for prop in properties:
            if not hasattr(self,prop) or not hasattr(other,prop):
                continue
            x = getattr(self,prop)
            y = getattr(other,prop)
            if x == y:
                continue
            if x > y:
                return 1
            else:
                return -1
            
        return 0

    def copy(self):
        """
        Make a copy of self (using deepcopy)
        
        :return: A Particle object identical to self
        """

        newPtc = copy.deepcopy(self)
        #Make sure all particles share the same comparison matrix
        if hasattr(self, 'cmpMatrix'):
            newPtc.cmpMatrix = self.cmpMatrix

        return newPtc

    def chargeConjugate(self,label=None):
        """
        Returns the charge conjugate particle (flips the sign of eCharge).        
        If it has a pdg property also flips its sign.
        If label is None, the charge conjugate name is defined as the original name plus "~" or
        if the original name ends in "+" ("-"), it is replaced by "-" ("+")

        :parameter label: If defined, defines the label of the charge conjugated particle.

        :return: the charge conjugate particle (Particle object)
        """
        
        pConjugate = self.copy()
        pConjugate._static = False #Temporarily set it to False to change attributes
        pConjugate.id = None

        if hasattr(self, 'cmpMatrix'):
            pConjugate.id = len(self.cmpMatrix[0]) #Set ID as the next entry in cmpMatrix
            #Add a column and a line to cmpMatrix with None
            for iline,line in enumerate(self.cmpMatrix):
                self.cmpMatrix[iline] = line + [None]
            self.cmpMatrix.append([None for i in range(len(self.cmpMatrix[0])+1)])
                    
        if hasattr(pConjugate, 'pdg') and pConjugate.pdg:
            pConjugate.pdg *= -1       
        if hasattr(pConjugate, 'eCharge') and pConjugate.eCharge:
            pConjugate.eCharge *= -1    
        if hasattr(pConjugate, 'label'):                
            if pConjugate.label[-1] == "+":
                pConjugate.label = pConjugate.label[:-1] + "-"
            elif pConjugate.label[-1] == "-":
                pConjugate.label = pConjugate.label[:-1] + "+"
            elif pConjugate.label[-1] == "~":
                pConjugate.label = pConjugate.label[:-1]
            else:
                pConjugate.label += "~"            
        
        if not label is None:
            pConjugate.label = label
            
        pConjugate._static = self._static #Restore the initial state

        return pConjugate

    def isNeutral(self):
        """
        Return True if the particle is electrically charged and color neutral.
        If these properties have not been defined, return True.
        
        :return: True/False
        """
        
        if hasattr(self,'eCharge') and self.eCharge != 0:
            return False
        if hasattr(self,'colordim') and self.colordim != 1:
            return False
        
        return True
    
    def isMET(self):
        """
        Checks if the particle can be considered as MET.
        If the isMET attribute has not been defined, it will return True/False is isNeutral() = True/False.
        Else it will return the isMET attribute.
        
        :return: True/False
        """
        
        if hasattr(self,'_isMET'):
            return self._isMET
        else:
            return self.isNeutral()

    def isPrompt(self):
        """
        Checks if the particle decays promptly (e.g. totalwidth = inf).

        :return: True/False
        """

        return self.totalwidth.asNumber() == float('inf')

    def isStable(self):
        """
        Checks if the particle is stable (e.g. totalwidth = 0).

        :return: True/False
        """

        return self.totalwidth.asNumber() == 0.
    
    def contains(self,particle):
        """
        If particle is a Particle object check if self and particle are the same object.

        :param particle: Particle or MultiParticle object

        :return: True/False
        """

        if self is particle:
            return True
        else:
            return False    



class MultiParticle(Particle):

    """ An instance of this class represents a list of particle object to allow for inclusive expresions such as jet. 
        The properties are: label, pdg, mass, electric charge, color charge, width 
    """
    
    def __init__(self, label, particles, **kwargs):

        """ 
        Initializes the particle list.
        """        

        self._static = False
        self.label = label
        self.particles = particles
        self.id = None
        Particle.__init__(self,**kwargs)
        self.setID()

    def __getattribute__(self,attr):
        """
        If MultiParticle does not have attribute, return a list
        if the attributes of each particle in self.particles.
        If not all particles have the attribute, it will raise an exception.
        If all particles share a common attribute, a single value
        will be returned.
         
        :parameter attr: Attribute string
         
        :return: Attribute or list with the attribute values in self.particles
        """
         
        try:
            return super(MultiParticle,self).__getattribute__(attr) #Python2
        except:
            pass

        try:
            return super().__getattribute__(attr) #Python3
        except:
            pass
         
        try:
            values = [getattr(particle,attr) for particle in self.particles]
            if all(type(x) == type(values[0]) for x in values):
                if all(x == values[0] for x in values):
                    return values[0]
            return values
        except:
            raise AttributeError

    def setID(self):
        """
        Defines the particle ID. If any of its particles has a comparison matrix,
        the ID will be defined as its dimension and the matrix will be extended.
        Otherwise the ID will be set to None.
        """

        cmpMatrix = None
        #Check if the comparison matrix has already been defined:
        try:
            cmpMatrix = self.cmpMatrix
        except AttributeError:
            pass

        #If not, try to see if any of the particles has the matrix:
        if cmpMatrix is None:
            for ptc in self.particles:
                if hasattr(ptc,'cmpMatrix'):
                    cmpMatrix = ptc.cmpMatrix
                    break

        if cmpMatrix is None:
            self.id = None
        else:
            self.id = len(self.cmpMatrix[0]) #Set ID as the next entry in cmpMatrix
            self.cmpMatrix = cmpMatrix
            #Add a column and a line to cmpMatrix with None
            for iline,line in enumerate(self.cmpMatrix):
                self.cmpMatrix[iline] = line + [None]
            self.cmpMatrix.append([None for i in range(len(self.cmpMatrix[0])+1)])
            
    def cmpProperties(self,other, 
                      properties = ['Z2parity','spin','colordim','eCharge','mass','totalwidth']):
        """
        Compares the properties in self with the ones in other.
        If other is a Particle object, checks if any of the particles in self matches
        other.
        If other is a MultiParticle object, checks if any particle in self matches
        any particle in other.
        If self and other are equal returns 0,
        else returns the result of comparing the first particle of self with other.
        
        :param other: a Particle or MultiParticle object
        :param properties: list with properties to be compared. Default is spin, colordim and eCharge
        
        :return: 0 if properties are equal, -1 if self < other and 1 if self > other.
        """
        
        #Check if any of its particles matches other
        if isinstance(other,Particle):
            otherParticles = [other]
        elif isinstance(other,MultiParticle):
            otherParticles = other.particles
            
        for otherParticle in otherParticles:
            if any(p.cmpProperties(otherParticle,properties) == 0 for p in self.particles):
                return 0
 
        cmpv = self.particles[0].cmpProperties(otherParticles[0],properties)
        return cmpv

    def __getstate__(self):
        """
        Override getstate method. Required for pickling.
        """  
        return self.__dict__

    def __setstate__(self, state):
        """
        Override setstate method. Required for pickling.
        """

        self._static = False
        self.__dict__.update(state)

    def __add__(self, other):
        """
        Define addition of two Particle objects
        or a Particle object and a MultiParticle object.
        The result is a MultiParticle object containing
        both particles.
        """

        if not isinstance(other,(MultiParticle,Particle)):
            raise TypeError("Can not add a Particle object to %s" %type(other))
        elif other is self or self.contains(other): #Check if other is self or a subset of self
            return self
        #Check if self is a subset of other
        if other.contains(self):
            return other        
        elif isinstance(other,MultiParticle):
            addParticles = other.particles
        elif isinstance(other,Particle):
            addParticles = [other]

        combinedParticles = [ptc for ptc in addParticles if not self.contains(ptc)]
        combinedParticles += self.particles[:]

        combined = MultiParticle(label = 'multiple', particles = combinedParticles)

        return combined
    
    def __radd__(self,other):
        return self.__add__(other)
    
    def __iadd__(self,other):
        
        if isinstance(other,MultiParticle):
            self.particles += [ptc for ptc in other.particles if not self.contains(ptc)]
        elif isinstance(other,Particle):
            if not self.contains(other):
                self.particles.append(other)
                #Reset ID, since the Multiparticle changed
                if hasattr(self, 'cmpMatrix'):
                    self.id = len(self.cmpMatrix[0]) #Set ID as the next entry in cmpMatrix
                    #Add a column and a line to cmpMatrix with None
                    for iline,line in enumerate(self.cmpMatrix):
                        self.cmpMatrix[iline] = line + [None]
                    self.cmpMatrix.append([None for i in range(len(self.cmpMatrix[0])+1)])
                else:
                    self.id = None

        return self

    def getPdgs(self):
        """
        pdgs appearing in MultiParticle
        :return: list of pgds of particles in the MultiParticle
        """
        
        pdgs = [particle.pdg for particle in self.particles]
        
        return pdgs
        
    def getLabels(self):
        """
        labels appearing in MultiParticle
        :return: list of labels of particles in the MultiParticle
        """
        
        labels = [particle.label for particle in self.particles]
        
        return labels
    
    def isNeutral(self):
        """
        Return True if ALL particles in particle list are neutral.
        
        :return: True/False
        """
        
        neutral = all(particle.isNeutral() for particle in self.particles)
        return neutral

    def isMET(self):
        """
        Checks if all the particles in self can be considered as MET.
        
        :return: True/False
        """
        
        met = all(particle.isMET() for particle in self.particles)
        return met

    def contains(self,particle):
        """
        Check if MultiParticle contains the Particle object or MultiParticle object.

        :param particle: Particle or MultiParticle object

        :return: True/False
        """

        if not isinstance(particle,(Particle,MultiParticle)):
            raise False
        elif isinstance(particle,MultiParticle):
            checkParticles = particle.particles
        else:
            checkParticles = [particle]

        for otherParticle in checkParticles:
            hasParticle = False
            for p in self.particles:
                if p.contains(otherParticle):
                    hasParticle = True
            if not hasParticle:
                return False

        return True