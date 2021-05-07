class cRIOSetpoint(dict):
    r"""Holds the information for a setpoint in the right format for the 
    cRIO webserver.
    
    Should be used in combination with setSetpoint and setMultipleSetpoints.

    Parameters
    ----------
    target \: str
        the tag name to be set to a new value
    setpoint \: int or float
        the setpoint to be sent 
    
    NOTE
    ----
    For setMultipleSetpoints a list of cRIOSetpoint must be used.
    """
    def __init__(self, target, setpoint):
        self["Tag"] = target
        self["Value"] = setpoint


class cRIOConfigurationPIDController(dict):
    r"""Holds the information for the configuration of a PID controller in the
    right format for the cRIO webserver.
    
    Should be used in combination with configurePIDController.

    Parameters
    ----------
    controller \: str
        the tag name of the controller, simply C-xxx
    pv \: str
        the tag name of the PV that should be maintained at the SP of the 
        controller
    cv \: str
        the tag name of the destination of the control action 
        for the controller
    """
    def __init__(self, controller, pv, cv):
        # According to the API documentation, the naming should follow the 
        # convention: "C-xxx Controller.lvclass".
        self["Controller"] = controller + " Controller.lvclass" 
        
        self["Configuration"] = {"PV Tag": pv,
                                 "CV Tag": cv}
