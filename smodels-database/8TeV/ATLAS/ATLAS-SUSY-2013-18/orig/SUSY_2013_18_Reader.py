# This script reads files given as 'input' format in the HEP data website.
# e.g. see ATLAS susy analyses.

"""
This function reads the X,Y and values from the input file.
It returns the three corresponding lists of objects.

First it creates a general list, for which the entries are the lines that are read, in form of a list:
i.e. ListOfLines = [   [x1,y1,z1] , [x2,y2,z2] , ... , [xn,yn,zn]   ]
Then it extracts the entries number 0,1 and 2 for each list, and fills the vectors XArrays, YArrays ... ZArrays, that are then returned.
Note that you have to adapt the numbers of verctor that are returned and read according to the numbers of columns present in the file.
num_col is the total number of entrie you need (x,y,z for efficiencies - x,y for exlusion lines)
column is the colomun that you need
"""
def Reading_Values(input,num_col,column):
    print 'Reading the values from the input file: ',input,' .The column containing the chosen values is number: ',column , ' . \n'
    ListOfLines = []
    inputFile = open(input,'r')
    for line in inputFile:
        if line[0] != '#' and line[0] != '*' and line[0] != '\n':
            #            print line
            lineElements = line.split(';')
            #           print lineElements;
            elementsList = []
            for element in lineElements:
                if element and element != '\n':
                    #fElement=float(element)
                   element = element.replace(' ','')
                   elementsList.append(element)
            ListOfLines.append(elementsList)
    inputFile.close()
    
    XArray = []
    YArray = []
    ZArray = []
    #    print ListOfLines

    # If saves in the third list the values contained in the colomun number you specified in the parameter 'column'.
    if(num_col ==3):
        for list in ListOfLines:
           XArray.append(list[0])
           YArray.append(list[1])
           ZArray.append(list[column-1])
        return XArray, YArray, ZArray

    elif(num_col ==2):
        if(column == num_col):
            for list in ListOfLines:
                XArray.append(list[0])
                YArray.append(list[1])
            return XArray, YArray



"""
This function produces the efficiency maps: it multiplies the values for acceptance and efficiency and creates the .txt files for each region
The input parameters are the two name of the Acc and Eff files;
topo and SR are used to create the name of the output files.
BE CAREFUL if you want to divide or not by 10.000   ( i.e. if the values given are in percentage or absolute ): you can state this option
by inputting a normalization value in Norm
"""
def Map_Multiplier(topo, SR, accFile, effFile,num_col,column, Norm):
    X1,Y1,Acc = Reading_Values(accFile,num_col,column)
    X2,Y2,Eff = Reading_Values(effFile,num_col,column)
    outputMap = open('EffMap_'+topo+"_"+SR+".txt",'w')
    outputMap.write('# MassX , MassY , Eff*Acc  '+'\n')
    for x1,y1,acc in zip(X1,Y1,Acc):
        for x2,y2,eff in zip(X2,Y2,Eff):
            if x1==x2 and y1==y2:
#   print x1 + ' ' + x2 + ' ' + y1 + ' ' + y2 + ' \n'  # just to check if the selected values from the two files matches
                outputMap.write(x1 + ' ' + y1 + ' ' +  str(float(acc)*float(eff)/Norm) + '\n')
    print "Map ",'EffMap_'+topo+"_"+SR+".txt", ' written!'



"""
This function simply rewrite in a file .dat that you want to plot, in a SModelS friendly format. It takes the values of the arrays from the Reading_Values function.
Give as parameters the two array you want to plot, and the name of the output file.
With 'type of data' you specify what kind of values are you extracting. 
"""
def Simple_Map_Producer(X,Y,Z,type_of_data,outputName):
    output = open(outputName+'.dat','w')
    output.write('# MassX , MassY ' + type_of_data+'\n')
    for x,y,z in zip(X,Y,Z):
        output.write(x+' '+y+' '+z+'\n')

def Simple_Exclusion_Producer(X,Y,type_of_data,outputName):
    output = open(outputName+'.dat','w')
    output.write('# MassX , MassY ' + type_of_data+'\n')
    for x,y in zip(X,Y):
        output.write(x+' '+y+'\n')


'''
    # ******************************************************************************************************************************************************************
    # Example of Usage ATLAS-SUSY-2013-09-eff
    
    
    
    accFile       =     ['SR3LHigh_Acc.txt','SR3Llow_Acc.txt','SR3b_Acc.txt','SR0b_Acc.txt','SR1b_Acc.txt']
    effFile       =     ['SR3LHigh_Eff.txt','SR3Llow_Eff.txt','SR3b_Eff.txt','SR0b_Eff.txt','SR1b_Eff.txt']
    topologies    =     ['T1tttt','T1tttt','T1tttt','T1tttt','T1tttt',]
    Regions       =     ['SR3LHigh','SR3Llow','SR3b','SR0b','SR1b']
    
    
    Map_Multiplier('T1tttt', 'SR3LHigh','Acc_T1tttt_Atlas09.txt', 'Eff_T1tttt_Atlas09.txt',3,3, 100)
    Map_Multiplier('T1tttt', 'SR3Llow', 'Acc_T1tttt_Atlas09.txt', 'Eff_T1tttt_Atlas09.txt',3,4, 100)
    Map_Multiplier('T1tttt', 'SR3b',    'Acc_T1tttt_Atlas09.txt', 'Eff_T1tttt_Atlas09.txt',3,5, 100)
    Map_Multiplier('T1tttt', 'SR0b',    'Acc_T1tttt_Atlas09.txt', 'Eff_T1tttt_Atlas09.txt',3,6, 100)
    Map_Multiplier('T1tttt', 'SR1b',    'Acc_T1tttt_Atlas09.txt', 'Eff_T1tttt_Atlas09.txt',3,7, 100)
    
    
    NB
    sometimes you have one single input file for all the regions (like in this case),
    other times you have different input files for different regions.
    '''



Map_Multiplier('T1bbbb'  , 'SR-0l-4j-A',    'Acc_fig5_T1bbbb.txt',    'Eff_fig5_T1bbbb.txt'       ,3,3, 10000)
Map_Multiplier('T1bbbb'  , 'SR-0l-4j-B',    'Acc_fig5_T1bbbb.txt',    'Eff_fig5_T1bbbb.txt'       ,3,4, 10000)
Map_Multiplier('T1bbbb'  , 'SR-0l-4j-C',    'Acc_fig5_T1bbbb.txt',    'Eff_fig5_T1bbbb.txt'       ,3,5, 10000)

Map_Multiplier('T1tttt'  , 'SR-0l-7j-A',    'Acc_fig13_T1tttt.txt',    'Eff_fig14_T1tttt.txt'       ,3,3, 10000)
Map_Multiplier('T1tttt'  , 'SR-0l-7j-B',    'Acc_fig13_T1tttt.txt',    'Eff_fig14_T1tttt.txt'       ,3,4, 10000)
Map_Multiplier('T1tttt'  , 'SR-0l-7j-C',    'Acc_fig13_T1tttt.txt',    'Eff_fig14_T1tttt.txt'       ,3,5, 10000)
Map_Multiplier('T1tttt'  , 'SR-1l-6j-A',    'Acc_fig13_T1tttt.txt',    'Eff_fig14_T1tttt.txt'       ,3,6, 10000)
Map_Multiplier('T1tttt'  , 'SR-1l-6j-B',    'Acc_fig13_T1tttt.txt',    'Eff_fig14_T1tttt.txt'       ,3,7, 10000)
Map_Multiplier('T1tttt'  , 'SR-1l-6j-C',    'Acc_fig13_T1tttt.txt',    'Eff_fig14_T1tttt.txt'       ,3,8, 10000)



T1tttt_X  , T1tttt_Y = Reading_Values('T1tttt_Exclusion_SingleLepton.txt',2,2)
T1bbbb_X  , T1bbbb_Y = Reading_Values('T1bbbb_Obs_Line.txt',2,2)
Simple_Exclusion_Producer(T1tttt_X,T1tttt_Y,'T1tttt ATLAS-SUSY-2013-18 Obs Exclusion','T1tttt_ATLAS-SUSY-2013-18-Obs_Excl')
Simple_Exclusion_Producer(T1bbbb_X,T1bbbb_Y,'T1bbbb ATLAS-SUSY-2013-18 Obs Exclusion','T1bbbb_ATLAS-SUSY-2013-18-Obs_Excl')

T1tttt_X , T1tttt_Y, T1tttt_UL = Reading_Values('T1tttt_UL_singleLepton.txt',3,3)
T1bbbb_X , T1bbbb_Y, T1bbbb_UL = Reading_Values('T1bbbb_XSecUL.txt',3,3)
Simple_Map_Producer(T1tttt_X,T1tttt_Y, T1tttt_UL,'T1tttt ATLAS-SUSY-2013-18 UL','T1tttt_ATLAS-SUSY-2013-18_UL')
Simple_Map_Producer(T1bbbb_X,T1bbbb_Y, T1bbbb_UL,'T1bbbb ATLAS-SUSY-2013-18 UL','T1bbbb_ATLAS-SUSY-2013-18_UL')








