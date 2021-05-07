import logging
logger = logging.getLogger(__name__)

from .cRIOExceptions import URLError, cRIOBadRequest, cRIOWebServiceInactive

def r200(response):
    logger.debug(f"Status code: {response.status_code} - Succes.")
    return True

def r400(response):
    logger.critical(f"Status code: {response.status_code} - Failed: Setting not accepted.")
    errorMessage = response.json()
    logger.critical(f"Response: {errorMessage}")
    raise cRIOBadRequest(errorMessage)

def r403(response):
    logger.critical(f"Status code: {response.status_code} - Failed: WebService on cRIO is inactive.")
    errorMessage = response.json()
    logger.critical(f"Response: {errorMessage}")
    raise cRIOWebServiceInactive(errorMessage)
    
def r404(response):
    logger.critical(f"Status code: {response.status_code} - Failed: Could not access {url} .")
    raise URLError(f"Could not access the cRIO.")

RESPONSES = {200: r200,
             400: r400,
             403: r403,
             404: r404}
