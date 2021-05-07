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

from .cRIOExceptions import URLError, cRIOBadRequest
from .cRIOFormats import cRIOSetpoint, cRIOConfigurationPIDController

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
        if r.status_code == 200:
            # TODO: No more degrees Celsius as symbol or m3 as symbol. Please degC and m^3!
            currentData = r.json()
            currentData = currentData["CurrentData"]
#            logger.critical(f"{command} resulted in a json without a key 'CurrentData'")
            
            logger.info(f"Processing results")
            currentValues = {}
            currentUnits = {}
            for k, v in currentData.items():
                currentValues[k] = v["Value"]
                currentUnits[k] = v["Unit"]
            currentUnits["cRIO Timestamp"] = currentData["cRIO Timestamp"]["Value"]
            logger.info(f"Converting results to pandas Series")
            return pd.Series(currentValues), pd.Series(currentUnits)
        else:
            logger.critical(f"Could not access {url} - status code: {r.status_code}")
            raise URLError(f"Could not access {url}")
 
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
        if r.status_code == 200:
             # TODO: No more degrees Celsius as symbol or m3 as symbol. Please degC and m^3!
            alarmSettings = r.json()
            return alarmSettings
        else:
            logger.critical(f"Could not access {url} - status code: {r.status_code}")
            raise URLError(f"Could not access {url}")
    
    def getSystemInformation(self):
        logger.info(f"Getting system information")
        command = self.COMMANDS["getSystemInformation"]
        url = self.ip + "/" + command
        logger.info(f"Accessing {url}")
        r = requests.get(url)
        if r.status_code == 200:
            systemSettings = r.json()
            return systemSettings
        else:
            logger.critical(f"Could not access {url} - status code: {r.status_code}")
            raise URLError(f"Could not access {url}")
 
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
        if r.status_code == 200:
            logger.debug("Setting setpoint succesful")
            return True
        elif r.status_code == 400:
            logger.critical(f"The setpoint was not accepted by the cRIO")
            errorMessage = r.json()
            logger.critical(f"Response: {errorMessage}")
            raise cRIOBadRequest(errorMessage)
        elif r.status_code == 404:
            logger.critical(f"Could not access {url} - status code: {r.status_code}")
            raise URLError(f"Failed to set setpoint")
        else:
            logger.critical(f"Unknown error on cRIO side")
            raise URLError(f"Failed to set setpoint")
            
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
        if r.status_code == 200:
            logger.debug("Setting setpoints succesful")
            return True
        elif r.status_code == 400:
            logger.critical(f"One or more of the setpoints were not accepted by the cRIO")
            errorMessage = r.json()
            logger.critical(f"Response: {errorMessage}")
            raise cRIOBadRequest(errorMessage)
        elif r.status_code == 404:
            logger.critical(f"Could not access {url} - status code: {r.status_code}")
            raise URLError(f"Failed to set setpoints")
        else:
            logger.critical(f"Unknown error on cRIO side")
            raise URLError(f"Failed to set setpoints")
    
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
        if r.status_code == 200:
            logger.debug("Switching of cRIO logging succesful")
            return True
        elif r.status_code == 400:
            logger.critical(f"Switching was not accepted by the cRIO")
            errorMessage = r.json()
            logger.critical(f"Response: {errorMessage}")
            raise cRIOBadRequest(errorMessage)
        elif r.status_code == 404:
            logger.critical(f"Could not access {url} - status code: {r.status_code}")
            raise URLError(f"Failed to switch logging")
        else:
            logger.critical(f"Unknown error on cRIO side")
            raise URLError(f"Failed to switch logging")
    
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
        if r.status_code == 200:
            logger.debug("Configuration succesful")
            return True
        elif r.status_code == 400:
            logger.critical(f"Configuration was not accepted by the cRIO")
            errorMessage = r.json()
            logger.critical(f"Response: {errorMessage}")
            raise cRIOBadRequest(errorMessage)
        elif r.status_code == 404:
            logger.critical(f"Could not access {url} - status code: {r.status_code}")
            raise URLError(f"Failed to configure controller")
        else:
            logger.critical(f"Unknown error on cRIO side")
            raise URLError(f"Failed to configure controller")
            

        

