#!/usr/bin/env python3

"""
.. module:: testPyhf
   :synopsis: Test the pyhfInterface module

.. moduleauthor:: Gael Alguero <gael.alguero@lpsc.in2p3.fr>

"""

import sys
sys.path.insert(0,"../")
import unittest
from smodels.tools.pyhfInterface import PyhfData, PyhfUpperLimitComputer

class PyhfTest(unittest.TestCase):

    def simpleJson(self, bkg, obs):
        """
        Define a simple likelihood model under the json format
        :param bkg: list of bkg numbers
        :param obs: list of ebserved numbers

        :return: a simple likelihood specification under the json dictionary
        """
        #Defining the channels
        modifiers = []
        modifiers.append(dict(data=None,
                              type='lumi',
                              name='lumi'))
        samples = [dict(name='bkg',
                        data=bkg,
                        modifiers=modifiers)]
        channels = [dict(name='SR1',
                         samples=samples)]
        # Defining the measurements
        config = dict(poi='mu_SIG',
                      parameters=[dict(auxdata=[1],
                                       bounds=[[0.915, 1.085]],
                                       inits=[1],
                                       sigmas=[0.017],
                                       name='lumi')])
        measurements = [dict(name='BasicMeasurement',
                             config=config)]
        # Defining the observations
        observations = [dict(name='SR1',
                             data=obs)]
        ws = dict(channels=channels,
                  measurements=measurements,
                  observations=observations,
                  version='1.0.0')
        return ws

    def testCorruptJson1Signal(self):
        """
        Tests how the module handles corrupted json files
        Maybe it is needed to test different types of corruptions
        """
        #Defining the channels
        modifiers = []
        modifiers.append(dict(data=None,
                              type='lumi',
                              name='lumi'))
        samples = [dict(name='bkg',
                        data=[10],
                        modifiers=modifiers)]
        channels = [dict(name='SR1',
                         samples=samples)]
        # Defining the measurements
        config = dict(poi='mu_SIG',
                      parameters=[dict(auxdata=[1],
                                       bounds=[[0.915, 1.085]],
                                       inits=[1],
                                       sigmas=[0.017],
                                       name='lumi')])
        measurements = [dict(name='BasicMeasurement',
                             config=config)]
        # Defining the observations
        observations = [dict(name='SR1',
                             data=[0.9])]
        # Missing channels
        ws = dict(#channels=channels,
                  measurements=measurements,
                  observations=observations,
                  version='1.0.0'
                  )
        data = PyhfData([[0.1]], [ws])
        ulcomputer = PyhfUpperLimitComputer(data)
        ul = ulcomputer.ulSigma()
        self.assertEqual(ulcomputer.workspaces, None)
        self.assertEqual(ul, None)
        # Missing measurements
        ws = dict(channels=channels,
                  #measurements=measurements,
                  observations=observations,
                  version='1.0.0'
                  )
        data = PyhfData([[0.1]], [ws])
        ulcomputer = PyhfUpperLimitComputer(data)
        ul = ulcomputer.ulSigma()
        self.assertEqual(ulcomputer.workspaces, None)
        self.assertEqual(ul, None)
        # Missing observations
        ws = dict(channels=channels,
                  measurements=measurements,
                  #observations=observations,
                  version='1.0.0'
                  )
        data = PyhfData([[0.1]], [ws])
        ulcomputer = PyhfUpperLimitComputer(data)
        ul = ulcomputer.ulSigma()
        self.assertEqual(ulcomputer.workspaces, None)
        self.assertEqual(ul, None)
        # Missing version
        ws = dict(channels=channels,
                  measurements=measurements,
                  observations=observations,
                  #version='1.0.0'
                  )
        data = PyhfData([[0.1]], [ws])
        ulcomputer = PyhfUpperLimitComputer(data)
        ul = ulcomputer.ulSigma()
        self.assertEqual(ulcomputer.workspaces, None)
        self.assertEqual(ul, None)

    def testCorruptJson2Signal(self):
        """
        Tests how the module handles corrupted json files
        Maybe it is needed to test different types of corruptions
        """
        #Defining the channels
        modifiers = []
        modifiers.append(dict(data=None,
                              type='lumi',
                              name='lumi'))
        samples = [dict(name='bkg',
                        data=[10, 9],
                        modifiers=modifiers)]
        channels = [dict(name='SR1',
                         samples=samples)]
        # Defining the measurements
        config = dict(poi='mu_SIG',
                      parameters=[dict(auxdata=[1],
                                       bounds=[[0.915, 1.085]],
                                       inits=[1],
                                       sigmas=[0.017],
                                       name='lumi')])
        measurements = [dict(name='BasicMeasurement',
                             config=config)]
        # Defining the observations
        observations = [dict(name='SR1',
                             data=[0.9, 0.8])]
        # Missing channels
        ws = dict(#channels=channels,
                  measurements=measurements,
                  observations=observations,
                  version='1.0.0'
                  )
        data = PyhfData([[0.1, 0.2]], [ws])
        ulcomputer = PyhfUpperLimitComputer(data)
        ul = ulcomputer.ulSigma()
        self.assertEqual(ulcomputer.workspaces, None)
        self.assertEqual(ul, None)
        # Missing measurements
        ws = dict(channels=channels,
                  #measurements=measurements,
                  observations=observations,
                  version='1.0.0'
                  )
        data = PyhfData([[0.1, 0.2]], [ws])
        ulcomputer = PyhfUpperLimitComputer(data)
        ul = ulcomputer.ulSigma()
        self.assertEqual(ulcomputer.workspaces, None)
        self.assertEqual(ul, None)
        # Missing observations
        ws = dict(channels=channels,
                  measurements=measurements,
                  #observations=observations,
                  version='1.0.0'
                  )
        data = PyhfData([[0.1, 0.2]], [ws])
        ulcomputer = PyhfUpperLimitComputer(data)
        ul = ulcomputer.ulSigma()
        self.assertEqual(ulcomputer.workspaces, None)
        self.assertEqual(ul, None)
        # Missing version
        ws = dict(channels=channels,
                  measurements=measurements,
                  observations=observations,
                  #version='1.0.0'
                  )
        data = PyhfData([[0.1, 0.2]], [ws])
        ulcomputer = PyhfUpperLimitComputer(data)
        ul = ulcomputer.ulSigma()
        self.assertEqual(ulcomputer.workspaces, None)
        self.assertEqual(ul, None)

    def testNoSignal(self):
        ws = self.simpleJson([0.9], [10])
        data = PyhfData([[0]], [ws])
        ulcomputer = PyhfUpperLimitComputer(data)
        ul = ulcomputer.ulSigma()
        self.assertEqual(ul, None)

    def testWrongNbOfSignals(self):
        # One single json but too much signals
        ws = self.simpleJson([0.9], [10])
        data = PyhfData([[0.9, 0.5]], [ws])
        ulcomputer = PyhfUpperLimitComputer(data)
        ul1 = ulcomputer.ulSigma()
        # Two jsons but only one signal
        ws = [self.simpleJson([0.9], [10]), self.simpleJson([0.8], [9])]
        data = PyhfData([[0.5]], ws)
        ulcomputer = PyhfUpperLimitComputer(data)
        ul2 = ulcomputer.ulSigma(workspace_index=0)
        self.assertEqual(ul1, None)
        self.assertEqual(ul2, None)

    def testWSindex(self):
        ws = [self.simpleJson([0.9], [10]), self.simpleJson([0.8], [9])]
        data = PyhfData([[0.1], [0.2]], ws)
        ulcomputer = PyhfUpperLimitComputer(data)
        ul = ulcomputer.ulSigma()
        self.assertEqual(ul, None)

if __name__ == "__main__":
    unittest.main()
