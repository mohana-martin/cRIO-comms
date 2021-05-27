# -*- coding: utf-8 -*-
"""
Created on Sat Sep 26 18:42:13 2020

@author: marti
"""

import abc

from copy import deepcopy

import requests

import pandas as pd

import logging
logger = logging.getLogger(__name__)

from .cRIOExceptions import *
from .cRIOFormats import cRIOSetpoint, cRIOConfigurationPIDController

from .cRIOResponses import RESPONSES

class cRIOCaryaABC(abc.ABC):
    

    def __init__(self, ip):
        self.ip = ip

    @property
    def ip(self):
        return deepcopy(self.__ip)

    @ip.setter
    def ip(self, v):
        self.__ip = v
        
    @abc.abstractmethod
    def getCurrentData():
        pass
#    
#    @abc.abstractmethod
#    def getSensorSettings():
#        pass

    @abc.abstractmethod
    def getAlarmInformation():
        pass

    @abc.abstractmethod
    def setSetpoint():
        pass
    
    @abc.abstractmethod
    def setMultipleSetpoints():
        pass
    
    @abc.abstractmethod
    def switchDataLogging():
        pass
    
    @abc.abstractmethod
    def configurePIDController():
        pass
    
class cRIOCaryaSim(cRIOCaryaABC):
    
    def __init__(self, file, **kwargs):
        self._file_ = file
        super().__init__(**kwargs)
    
    def getCurrentData(self):
        df = pd.read_excel(self._file_, index_col=0)
        return df["VALUE"], df["UNITS"]
    
    def setSetpoint(self, setpoint):
        print(f"Changed setpoint of {setpoint['Tag']} to {setpoint['Value']}")
    
    def getAlarmInformation():
        pass
    
    def setMultipleSetpoints():
        pass

    def switchDataLogging():
        pass
    
    def configurePIDController():
        pass
    

class cRIOCaryaV1(cRIOCaryaABC):
    r"""Version 1 of the cRIO webserver API client.

    Holds the IP address of the cRIO webserver as well as the functionality
    related to getting data and sending setpoints and system settings.

    Parameters
    ----------
    ip \: str
        a string path pointing to the webserver.
    """
    def __init__(self, **kwargs):
        print(kwargs)
        super().__init__(**kwargs)
        self.COMMANDS = {"getCurrentData": r"CurrentData",
                          "getSystemInformation": r"SystemInformation",
                          "getAlarmInformation": r"AlarmInformation",
                          "setSetpoint": r"/SetSetpoint",
                          "setMultipleSetpoints": r"SetMultipleSetpoints",
                          "switchDataLogging": r"SwitchDataLogging",
                          "configurePIDController": r"ConfigurePIDController"}

    def getCurrentData(self):
        r"""Get the latest data held by the cRIO.

        Sends the respective command to get the latest data from the cRIO 
        webserver.
              
        Returns
        -------
        pandas.DataFrame
            index being the tag name, values containing the values
        pandas.DataFrame
            index being the tag name, values containing the units
            
        NOTE
        ----
        Raises URLError if unsucceeded in communication, KeyError if 
        unsucceeded in processing of the response.
        """
        logger.info(f"Getting current data")
        command = self.COMMANDS["getCurrentData"]
        url = self.ip + "/" + command
        logger.info(f"Accessing {url}")
        r = requests.get(url)
        
        if r.status_code in RESPONSES:
            currentData = RESPONSES[r.status_code](r).json()
            currentData = currentData["CurrentData"]
            currentValues = {}
            currentUnits = {}
            for k, v in currentData.items():
                currentValues[k] = v["Value"]
                currentUnits[k] = v["Unit"]
            currentUnits["cRIO Timestamp"] = currentData["cRIO Timestamp"]["Value"]
            logger.info(f"Converting results to pandas Series")
            return pd.Series(currentValues), pd.Series(currentUnits)
        else:
            raise cRIOUnknownStatusCode(r.status_code)
 
    def getAlarmInformation(self):
        r"""Get Alarm information from the cRIO.
        
        Returns
        -------
        numpy array
            error of the transformed value
            
        NOTE
        ----
        Raises URLError if unsucceeded in communication.
        """
        command = self.COMMANDS["getAlarmInformation"]
        logger.info(f"Getting alarm information")
        url = self.ip + "/" +command
        logger.info(f"Accessing {url}")
        r = requests.get(url)

        if r.status_code in RESPONSES:
            return RESPONSES[r.status_code](r).json()
        else:
            raise cRIOUnknownStatusCode(r.status_code)
    
    def getSystemInformation(self):
        logger.info(f"Getting system information")
        command = self.COMMANDS["getSystemInformation"]
        url = self.ip + "/" + command
        logger.info(f"Accessing {url}")
        r = requests.get(url)

        if r.status_code in RESPONSES:
            return RESPONSES[r.status_code](r).json()
        else:
            raise cRIOUnknownStatusCode(r.status_code)
 
    def setSetpoint(self, setpoint):
        r"""Set one setpoint on the cRIO.
        
        Parameters
        ----------
        setpoint \: cRIOSetpoint or dict
            contains the setpoint in the format as required by the API
        
        NOTE
        ----
        Raises URLError if unsucceeded in communication or cRIOBadRequest if
        the setpoint was not accepted by the cRIO.
        """
        logger.info(f"Setting setpoint: {setpoint}")
        command = self.COMMANDS["setSetpoint"]
        url = self.ip + "/" + command
        logger.info(f"Accessing {url}")
        r = requests.put(url, json=setpoint)

        if r.status_code in RESPONSES:
            return RESPONSES[r.status_code](r)
        else:
            raise cRIOUnknownStatusCode(r.status_code)
            
    def setMultipleSetpoints(self, setpoints):
        r"""Set one or more setpoints on the cRIO.
        
        Parameters
        ----------
        setpoint \: list
            contains the setpoints (cRIOSetpoint or dict) in the format as 
            required by the API
        
        NOTE
        ----
        Raises URLError if unsucceeded in communication or cRIOBadRequest if
        the setpoint was not accepted by the cRIO.
        """        
        logger.info(f"Setting multiple setpoints: {setpoints}")
        command = self.COMMANDS["setMultipleSetpoints"]
        url = self.ip + "/" + command
        logger.info(f"Accessing {url}")
        r = requests.put(url, json=setpoints)

        if r.status_code in RESPONSES:
            return RESPONSES[r.status_code](r)
        else:
            raise cRIOUnknownStatusCode(r.status_code)
    
    def switchDataLogging(self, datalogging=True):
        r"""Turn the internal datalogging on the cRIO On-Off.
        
        Parameters
        ----------
        datalogging \: bool
            Default ``True``
        
        NOTE
        ----
        Raises URLError if unsucceeded in communication or cRIOBadRequest if
        the setpoint was not accepted by the cRIO.
        """
        logger.info(f"Switching cRIO internal data logging to {datalogging}")
        command = self.COMMANDS["switchDataLogging"]
        url = self.ip + "/" + command
        logger.debug(f"Accessing {url}")
        r = requests.put(url, json={"On?":datalogging})

        if r.status_code in RESPONSES:
            return RESPONSES[r.status_code](r)
        else:
            raise cRIOUnknownStatusCode(r.status_code)
    
    def configurePIDController(self, configuration):
        r"""Configure one of the PID controllers that is running on the cRIO.
        
        Parameters
        ----------
        configuration \: cRIOConfigurationPIDController or dict
            contains the configuation in the format as required by the API
        
        NOTE
        ----
        Raises URLError if unsucceeded in communication.
        """
        logger.info(f"Configuring controller: {configuration}")
        command = self.COMMANDS["configurePIDController"]
        url = self.ip + "/" + command
        logger.info(f"Accessing {url}")
        r = requests.put(url, json=configuration)

        if r.status_code in RESPONSES:
            return RESPONSES[r.status_code](r)
        else:
            raise cRIOUnknownStatusCode(r.status_code)

cRIOWebServerComms = cRIOCaryaV1