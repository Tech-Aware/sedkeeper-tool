import sys
from typing import Optional, Dict, List, Callable, Any
from functools import wraps
import logging

from pysatochip.CardConnector import (CardConnector, CardNotPresentError, PinRequiredError, WrongPinError,
                                                 PinBlockedError, UnexpectedSW12Error, CardSetupNotDoneError,
                                                 UninitializedSeedError, ApduError, SeedKeeperError,
)

from log_config import get_logger, SUCCESS, setup_logging
from exceptions import (CardError, ControllerError, ViewError, FrameError, UIElementError, InitializationError,
                        ButtonCreationError, MainMenuError)

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
        logger.setLevel(loglevel)
        self.view = view
        self.view.controller = self

        try:
            self.cc = CardConnector(self, loglevel=loglevel)
            logger.info("CardConnector initialized successfully.")
        except Exception as e:
            logger.error("Failed to initialize CardConnector.", exc_info=True)
            raise ControllerError from e

        # card infos
        self.card_status = None

    @log_method
    def get_card_status(self):
        if self.cc.card_present:
            logger.info("In get_card_status")
            try:
                response, sw1, sw2, self.card_status = self.cc.card_get_status()
                if self.card_status:
                    logger.log(SUCCESS, f"Card satus: {self.card_status}")
                else:
                    logger.error(f"Failed to retrieve card_status")

                self.card_status[
                    'applet_full_version_string'] = f"{self.card_status['protocol_major_version']}.{self.card_status['protocol_minor_version']}-{self.card_status['applet_major_version']}.{self.card_status['applet_minor_version']}"
                return self.card_status

            except Exception as e:
                logger.error(f"Failed to retrieve card status: {e}")
                self.card_status = None
                return None

    @log_method
    def get_seedkeeper_status(self):
        if not self.cc.card_present:
            raise CardNotPresentError("No card found! Please insert card.")

        logger.info("Fetching card status")
        try:
            response, sw1, sw2, seedKeeper_status = self.cc.seedkeeper_get_status()
            if seedKeeper_status:
                logger.debug(f"Card status: {seedKeeper_status}")
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


    def PIN_dialog(self, msg):
        try:
            logger.info("Entering PIN_dialog method")

            def switch_unlock_to_false_and_quit():
                self.view.spot_if_unlock = False
                self.request('welcome')
                self.request('update_status')

            while True:
                try:
                    logger.debug("Requesting passphrase")
                    pin = self.request('get_passphrase', msg)
                    logger.debug(f"Passphrase received: pin={'***' if pin else None}")

                    if pin is None:
                        logger.info("Passphrase request cancelled or window closed")
                        self.request("show", "INFO", 'Device cannot be unlocked without PIN code!', 'Ok',
                                     lambda: switch_unlock_to_false_and_quit(), "./pictures_db/change_pin_popup_icon.jpg")
                        break

                    elif len(pin) < 4:
                        logger.warning("PIN length is less than 4 characters")
                        msg = "PIN must have at least 4 characters."
                        self.request("show", "INFO", msg, 'Ok',
                                     None, "./pictures_db/icon_change_pin_popup.jpg")

                    elif len(pin) > 64:
                        logger.warning("PIN length is more than 64 characters")
                        msg = "PIN must have less than 64 characters."
                        self.request("show", "INFO", msg, 'Ok',
                                     None, "./pictures_db/icon_change_pin_popup.jpg")

                    else:
                        logger.info("PIN length is valid")
                        pin = pin.encode('utf8')
                        try:
                            self.cc.card_verify_PIN_simple(pin)
                            break
                        except Exception as e:
                            logger.info("exception from pin dialog")
                            self.request('show', 'ERROR', str(e), 'Ok', None,
                                         "./pictures_db/icon_change_pin_popup.jpg")

                except Exception as e:
                    logger.error(f"An error occurred while requesting passphrase: {e}", exc_info=True)
                    return (False, None)

        except Exception as e:
            logger.critical(f"An unexpected error occurred in PIN_dialog: {e}", exc_info=True)
            return (False, None)

    @log_method
    def retrieve_secrets_stored_into_the_card(self) -> Dict[str, Any]:
        try:
            if self.cc.is_pin_set():
                self.cc.card_verify_PIN_simple()
            else:
                self.PIN_dialog(f'Unlock your {self.cc.card_type}')
            headers = self.cc.seedkeeper_list_secret_headers()
            logger.log(SUCCESS, f"Secrets retrieved successfully: {headers}")
            return self._format_secret_headers(headers)
        except Exception as e:
            logger.error(f"Error retrieving secrets: {e}")
            raise ControllerError(f"Failed to retrieve secrets: {e}")

    def _format_secret_headers(self, headers: List[Dict[str, Any]]) -> Dict[str, Any]:
        dic_type = {
            0x30: 'BIP39 mnemonic',
            0x40: 'Electrum mnemonic',
            0x10: 'Masterseed',
            0x70: 'Public Key',
            0x90: 'Password',
            0xA0: 'Authentikey certificate',
            0xB0: '2FA secret'
        }

        formatted_headers = []
        for header in headers:
            formatted_header = {
                'id': header['id'],
                'type': dic_type.get(header['type'], hex(header['type'])),
                'label': header['label']
            }
            formatted_headers.append(formatted_header)

        return {
            'num_secrets': len(headers),
            'headers': formatted_headers
        }

    def retrieve_details_about_secret_selected(self, secret_id):

        dic_type = {
            0x30: 'BIP39 mnemonic',
            0x40: 'Electrum mnemonic',
            0x10: 'Masterseed',
            0x70: 'Public Key',
            0x90: 'Password',
            0xA0: 'Authentikey certificate',
            0xB0: '2FA secret'
        }

        secret_details = self.cc.seedkeeper_export_secret(secret_id)
        logger.log(SUCCESS, f"Secret details: {secret_details}")
        formatted_details = {
            'label': secret_details['label'],
            'type': dic_type.get(secret_details['type'], hex(secret_details['type'])),
            'secret': secret_details['secret']
        }
        return formatted_details


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