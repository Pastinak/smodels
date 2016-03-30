"""
.. module:: datasetObj
   :synopsis: Holds the classes and methods used to read and store the information in the
              data folders.

.. moduleauthor:: Andre Lessa <lessa.a.p@gmail.com>

"""


import logging,os,glob
from smodels.experiment import txnameObj,infoObj
from smodels.tools import statistics
from smodels.tools.physicsUnits import fb
from smodels.experiment.exceptions import SModelSExperimentError as SModelSError

FORMAT = '%(levelname)s in %(module)s.%(funcName)s() in %(lineno)s: %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger(__name__)

logger.setLevel(level=logging.ERROR)


class DataSet(object):
    """Holds the information to a data set folder (TxName objects, dataInfo,...)
    """
        
    def __init__(self, path=None, info=None, createInfo=True ):
        
        self.path = path
        self.globalInfo = info
        self.txnameList = []
        
        if path and createInfo:
            logger.debug('Creating object based on data folder : %s' %self.path)
            
            #Get data folder info:
            if not os.path.isfile(os.path.join(path,"dataInfo.txt")):
                logger.error("dataInfo.txt file not found in " + path)
                raise TypeError
            self.dataInfo = infoObj.Info(os.path.join(path,"dataInfo.txt"))

            #Get list of TxName objects:
            for txtfile in glob.iglob(os.path.join(path,"*.txt")):
                try:                
                    txname = txnameObj.TxName(txtfile,self.globalInfo)
                    self.txnameList.append(txname)
                except TypeError: continue
            
    def __ne__ ( self, other ):
        return not self.__eq__ ( other )

    def __eq__ ( self, other ):
        if self.dataInfo != other.dataInfo:
            return False
        if len(self.txnameList ) != len ( other.txnameList ):
            return False
        #for (mytx, othertx) in zip ( self.txnameList, other.txnameList ):
        #    if mytx != othertx:
        #        return False
        return True

    def getValuesFor(self,attribute=None):
        """
        Returns a list for the possible values appearing in the DataSet
        for the required attribute.

        
        :param attribute: name of a field in the database (string). If not defined
                          it will return a dictionary with all fields and their respective
                          values
        :return: list of values
        """
        
        
        fieldDict = self.__dict__.items()[:]
        valuesDict = {}
        while fieldDict:
            for field,value in fieldDict[:]:
                if not '<smodels.experiment' in str(value):
                    if not field in valuesDict: valuesDict[field] = [value]
                    else: valuesDict[field].append(value)              
                else:
                    if isinstance(value,list):
                        for entry in value: fieldDict += entry.__dict__.items()[:]
                    else: fieldDict += value.__dict__.items()[:]
                fieldDict.remove((field,value))                

        #Try to keep only the set of unique values
        for key,val in valuesDict.items():
            try: valuesDict[key] = list(set(val))
            except: pass
        if not attribute: return valuesDict
        elif not attribute in valuesDict:
            logger.warning("Could not find field %s in database" % attribute)
            return False
        else:
            return valuesDict[attribute]
            

    def getAttributes(self,showPrivate=False):
        """
        Checks for all the fields/attributes it contains as well as the
        attributes of its objects if they belong to smodels.experiment.
        
        :param showPrivate: if True, also returns the protected fields (_field)
        :return: list of field names (strings)
        """
        
        fields = self.getValuesFor().keys()
        fields = list(set(fields))
        
        if not showPrivate:
            for field in fields[:]:
                if "_" == field[0]: fields.remove(field)
               
        return fields
    
    
    def getSRUpperLimit(self,alpha = 0.05, expected = False, compute = False ):
        """
        Computes the 95% upper limit on the signal*efficiency for a given
        dataset (signal region)
        Only to be used for efficiency map type results.
        :param alpha: Can be used to change the C.L. value. The default value is 0.05 (= 95% C.L.)
        :param expected: Compute expected limit ( i.e. Nobserved = NexpectedBG )
        :param compute: If True, the upper limit will be computed
                        from expected and observed number of events. If False, the value listed
                        in the database will be used instead.
        
        :return: upper limit value 
        """
        
        if not self.dataInfo.dataType == 'efficiencyMap':
            logger.error("getSRUpperLimit can only be used for efficiency map results!")
            raise SModelSError()
        
        if not compute:
            if expected:
                try:
                    return self.dataInfo.expectedUpperLimit
                except AttributeError:                    
                    logger.info("expectedUpperLimit field not found. Using observed UL instead.")
                    return self.dataInfo.upperLimit
            else:
                return self.dataInfo.upperLimit
        
        Nobs = self.dataInfo.observedN  #Number of observed events
        if expected: 
            Nobs = self.dataInfo.expectedBG 
        Nexp = self.dataInfo.expectedBG  #Number of expected BG events
        bgError = self.dataInfo.bgError # error on BG
        lumi = self.globalInfo.lumi
        if (lumi*fb).normalize()._unit:
            ID = self.globalInfo.id
            logger.error("Luminosity defined with wrong units for %s" %(ID) )
            return False
            
        maxSignalXsec = statistics.upperLimit(Nobs,Nexp,bgError,lumi,alpha)
        
                
        return maxSignalXsec
            
    