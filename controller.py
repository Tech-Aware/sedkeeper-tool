import sys
from typing import Optional, Dict, List, Callable
from functools import wraps
import logging

from pysatochip.pysatochip.CardConnector import (
    CardConnector,
    CardNotPresentError, PinRequiredError, WrongPinError,
    PinBlockedError, UnexpectedSW12Error, CardSetupNotDoneError,
    UninitializedSeedError, ApduError
)

from log_config import get_logger, SUCCESS, setup_logging
from exceptions import SeedkeeperError, CardError, ControllerError, ViewError, FrameError, UIElementError, \
    InitializationError, ButtonCreationError, MainMenuError

logger = get_logger(__name__)


def log_method(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(f"Entering {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"Exiting {func.__name__}")
            return result
        except Exception as e:
            logger.exception(f"Exception in {func.__name__}: {e}")
            raise

    return wrapper


class Controller:
    @log_method
    def __init__(self, cc, view, loglevel=logging.INFO):
        try:
            super().__init__()
            self._initialize_attributes()
            self.view = view
            self.view.controller = self
            try:
                self.cc = CardConnector(self, loglevel=loglevel)
                logger.log(SUCCESS, "CardConnector initialized successfully.")
            except Exception as e:
                logger.error("Failed to initialize CardConnector.", exc_info=True)
                raise ControllerError(f"Failed to initialize CardConnector {e}") from e
            logger.log(SUCCESS, "Controller initialization completed successfully")
        except Exception as e:
            logger.critical("Failed to initialize Controller", exc_info=True)
            raise ControllerError(f"Failed to initialize Controller: {e}") from e

    @log_method
    def _initialize_attributes(self):
        self.card_present: Optional[bool] = None
        self.card_type: Optional[str] = None
        self.card_version: Optional[str] = None
        self.needs2FA: Optional[bool] = None
        self.is_seeded: Optional[bool] = None
        self.setup_done: Optional[bool] = None
        self.card_label: Optional[str] = None
        self.pin_left: Optional[int] = None
        self.two_FA: Optional[bool] = None
        self.number_secrets: Optional[int] = None
        self.total_memory: Optional[int] = None
        self.free_memory: Optional[int] = None
        self.total_numbers_log: Optional[int] = None
        self.available_log_number: Optional[int] = None
        self.last_log: Optional[str] = None

        if hasattr(self, 'cc') and self.cc.card_type == "SeedKeeper":
            self.truststore: Dict = {}
            self.card_event: bool = False

    @log_method
    def get_card_status(self):
        if not self.cc.card_present:
            raise CardNotPresentError("No card found! Please insert card.")

        logger.info("Fetching card status")
        try:
            response, sw1, sw2, d = self.cc.card_get_status()
            if d:
                logger.debug(f"Card status: {d}")
                self.card_present = True
                self.card_type = self.cc.card_type
                self.card_version = d['applet_major_version']
                self.needs2FA = d['needs2FA']
                self.is_seeded = d['is_seeded']
                self.setup_done = d['setup_done']
                self.pin_left = d['PIN0_remaining_tries']
                self.two_FA = d['needs2FA']
                return (self.card_present, self.card_version, self.needs2FA, self.is_seeded,
                        self.setup_done, self.card_type, self.pin_left)
            else:
                raise CardSetupNotDoneError("Failed to retrieve card status")
        except Exception as e:
            logger.error(f"Error fetching card status: {e}")
            raise

    @log_method
    def get_seedkeeper_status(self):
        if not self.cc.card_present:
            raise CardNotPresentError("No card found! Please insert card.")

        logger.info("Fetching card status")
        try:
            response, sw1, sw2, seedKeeper_status = self.cc.seedkeeper_get_status()
            if seedKeeper_status:
                logger.debug(f"Card status: {d}")
                self.number_secrets = seedKeeper_status['nbr_secrets']
                self.total_memory = seedKeeper_status['total_memory']
                self.free_memory = seedKeeper_status['free_memory']
                self.total_numbers_log = seedKeeper_status['nb_logs_total']
                self.available_log_number = seedKeeper_status['nb_logs_avail']
                self.last_log = seedKeeper_status['last_log']
                return (self.number_secrets, self.total_memory, self.free_memory, self.total_numbers_log, self.available_log_number,
                        self.last_log)
            else:
                raise CardSetupNotDoneError("Failed to retrieve card status")
        except Exception as e:
            logger.error(f"Error fetching card status: {e}")
            raise ApduError(f"Error fetching card status: {e}")



    @log_method
    def request(self, request_type: str, *args):
        logger.info(f"Processing request: {request_type}")
        method = getattr(self.view, request_type, None)
        if method:
            return method(*args)
        else:
            logger.error(f"Unknown request type: {request_type}")
            raise ControllerError(f"Unknown request type: {request_type}")

    @log_method
    def verify_pin(self, pin: str):
        try:
            self.cc.card_verify_PIN_simple(pin)
            logger.log(SUCCESS, "PIN verified successfully")
        except WrongPinError as e:
            logger.warning(f"Wrong PIN entered: {e}")
            raise
        except PinBlockedError as e:
            logger.error(f"PIN blocked: {e}")
            raise
        except UnexpectedSW12Error as e:
            logger.error(f"Unexpected error during PIN verification: {e}")
            raise

    # Autres méthodes du contrôleur...


if __name__ == "__main__":
    setup_logging()
    try:
        # Ici, vous devriez initialiser votre vue et passer la vue au contrôleur
        # view = View()
        # controller = Controller(view)
        # Ensuite, vous pouvez exécuter votre application
        pass
    except Exception as e:
        logger.critical(f"Application failed to start: {e}", exc_info=True)
        sys.exit(1)