import sys
import os
from typing import Optional, Dict, List, Callable, Any
from functools import wraps
import logging
import json
from mnemonic import Mnemonic

from pysatochip.CardConnector import (CardConnector, CardNotPresentError, PinRequiredError, WrongPinError,
                                                 PinBlockedError, UnexpectedSW12Error, CardSetupNotDoneError,
                                                 UninitializedSeedError, ApduError, SeedKeeperError,
)

from log_config import get_logger, SUCCESS, setup_logging, log_method
from exceptions import *
logger = get_logger(__name__)


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

    ####################################################################################################################
    """PIN MANAGEMENT"""
    ####################################################################################################################
    @log_method
    def card_setup_native_pin(self, pin: str) -> bool:
        try:
            logger.info("001 Starting card_setup_native_pin method")
            logger.info("002 Setting up card PIN and applet references")

            pin_0: List = list(pin)
            pin_tries_0: int = 0x05
            ublk_tries_0: int = 0x01
            ublk_0: List[int] = list(os.urandom(16))  # PUK code
            pin_tries_1: int = 0x01
            ublk_tries_1: int = 0x01
            pin_1: List[int] = list(os.urandom(16))  # Second pin
            ublk_1: List[int] = list(os.urandom(16))
            secmemsize: int = 32  # Number of slots reserved in memory cache
            memsize: int = 0x0000  # RFU
            create_object_ACL: int = 0x01  # RFU
            create_key_ACL: int = 0x01  # RFU
            create_pin_ACL: int = 0x01  # RFU

            logger.info("003 Sending setup native PIN command to card")
            response, sw1, sw2 = self.cc.card_setup(
                pin_tries_0, ublk_tries_0, pin_0, ublk_0,
                pin_tries_1, ublk_tries_1, pin_1, ublk_1,
                secmemsize, memsize,
                create_object_ACL, create_key_ACL, create_pin_ACL
            )
            logger.info(f"004 Response from card: {response}, sw1: {hex(sw1)}, sw2: {hex(sw2)}")

            if sw1 != 0x90 or sw2 != 0x00:
                error_msg = f"Unable to set up applet! sw12={hex(sw1)} {hex(sw2)}"
                logger.warning(f"005 {error_msg}")
                self.view.show("ERROR", error_msg, "Ok", None, "./pictures_db/change_pin_popup_icon.jpg")
                return False
            else:
                logger.log(SUCCESS, "006 Applet setup successfully")
                self.setup_done = True
                self.view.update_status()
                self.view.show_view_start_setup()
                return True

        except Exception as e:
            logger.error(f"007 Unexpected error in card_setup_native_pin: {e}", exc_info=True)
            self.view.show("ERROR", "An unexpected error occurred during PIN setup", "Ok", None,
                           "./pictures_db/change_pin_popup_icon.jpg")
            raise ControllerError(f"008 Failed to set up native PIN: {e}") from e

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
                    pin = self.view.get_passphrase(msg)
                    logger.debug(f"Passphrase received: pin={'***' if pin else None}")

                    if pin is None:
                        logger.info("Passphrase request cancelled or window closed")
                        self.view.show("INFO", 'Device cannot be unlocked without PIN code!', 'Ok',
                                     lambda: switch_unlock_to_false_and_quit(), "./pictures_db/change_pin_popup_icon.jpg")
                        break

                    elif len(pin) < 4:
                        logger.warning("PIN length is less than 4 characters")
                        msg = "PIN must have at least 4 characters."
                        self.view.show("INFO", msg, 'Ok',
                                     None, "./pictures_db/change_pin_popup_icon.jpg")

                    elif len(pin) > 64:
                        logger.warning("PIN length is more than 64 characters")
                        msg = "PIN must have less than 64 characters."
                        self.view.show("INFO", msg, 'Ok',
                                     None, "./pictures_db/change_pin_popup_icon-icon.jpg")

                    else:
                        logger.info("PIN length is valid")
                        pin = pin.encode('utf8')
                        try:
                            if self.cc.setup_done:
                                self.cc.card_verify_PIN_simple(pin)
                            else:
                                self.card_setup_native_pin(pin)
                            break
                        except Exception as e:
                            logger.info("exception from pin dialog")
                            self.request('show', 'ERROR', str(e), 'Ok', None,
                                         "./pictures_db/change_pin_popup_icon.jpg")

                except Exception as e:
                    logger.error(f"An error occurred while requesting passphrase: {e}", exc_info=True)
                    return (False, None)

        except Exception as e:
            logger.critical(f"An unexpected error occurred in PIN_dialog: {e}", exc_info=True)
            return (False, None)


    @log_method
    def change_card_pin(self, current_pin, new_pin, new_pin_confirm):
        try:
            logger.info("001 Starting change_card_pin method")

            if not self.cc.card_present or self.cc.card_type == "Satodime":
                logger.warning("002 Card not present or incompatible card type")
                raise CardNotSuitableError("Card not present or incompatible card type")

            if len(new_pin) < 4:
                logger.warning("003 New PIN is too short")
                raise InvalidPinError("PIN must contain at least 4 characters")

            if new_pin != new_pin_confirm:
                logger.warning("004 New PINs do not match")
                raise PinMismatchError("The PIN values do not match!\n Please type PIN again!")

            current_pin_bytes = list(current_pin.encode('utf8'))
            new_pin_bytes = list(new_pin.encode('utf8'))

            response, sw1, sw2 = self.cc.card_change_PIN(0, current_pin_bytes, new_pin_bytes)

            if sw1 == 0x90 and sw2 == 0x00:
                logger.log(SUCCESS, "005 PIN changed successfully")
                self.view.show("SUCCESS", "PIN changed successfully!", "Ok",
                               lambda: self.view.show_view_start_setup(),
                               "./pictures_db/change_pin_popup_icon.jpg")
                return True
            else:
                error_msg = f"Failed to change PIN with error code: {hex(sw1)}{hex(sw2)}\nProbably too long"
                logger.error(f"006 {error_msg}")
                raise PinChangeError(error_msg)

        except CardNotSuitableError as e:
            logger.error(f"007 CardNotSuitableError: {e}")
            self.view.show("ERROR", str(e), "Ok", None, "./pictures_db/change_pin_popup_icon.jpg")
        except InvalidPinError as e:
            logger.error(f"008 InvalidPinError: {e}")
            self.view.show("ERROR", str(e), "Ok", None, "./pictures_db/change_pin_popup_icon.jpg")
        except PinMismatchError as e:
            logger.error(f"009 PinMismatchError: {e}")
            self.view.show("WARNING", str(e), "Ok", None, "./pictures_db/change_pin_popup_icon.jpg")
        except PinChangeError as e:
            logger.error(f"010 PinChangeError: {e}")
            self.view.show("ERROR", str(e), "Ok", None, "./pictures_db/change_pin_popup_icon.jpg")
        except Exception as e:
            logger.error(f"011 Unexpected error in change_card_pin: {e}", exc_info=True)
            self.view.show("ERROR", "An unexpected error occurred\n during PIN change", "Ok", None,
                           "./pictures_db/change_pin_popup_icon.jpg")

        return False

    @log_method
    def edit_label(self, label):
        try:
            logger.info("001 Starting edit_label method")
            logger.info(f"002 New label to set: {label}")

            response, sw1, sw2 = self.cc.card_set_label(label)

            if sw1 == 0x90 and sw2 == 0x00:
                logger.log(SUCCESS, f"003 New label set successfully: {label}")
                self.view.show(
                    "SUCCESS",
                    "New label set successfully",
                    "Ok",
                    self.view.view_start_setup,
                    "./pictures_db/edit_label_icon_ws.jpg"
                )
            else:
                error_code = hex(sw1 * 256 + sw2)
                logger.warning(f"004 Failed to set new label. Error code: {error_code}")
                self.view.show(
                    "ERROR",
                    f"Failed to set label (code {error_code})",
                    "Ok",
                    None,
                    "./pictures_db/edit_label_icon_ws.jpg"
                )

            logger.log(SUCCESS, "005 edit_label method completed")
        except Exception as e:
            logger.error(f"006 Unexpected error in edit_label: {e}", exc_info=True)
            self.view.show(
                "ERROR",
                f"Failed to edit label: {e}",
                "Ok",
                None,
                "./pictures_db/edit_label_icon_ws.jpg"
            )
            raise ControllerError(f"007 Failed to edit label: {e}") from e

    @log_method
    def get_card_label_infos(self) -> Optional[str]:
        """
        Get the label information from the card.

        Returns:
            Optional[str]: The card label if present, None if no card or no label.
        """
        try:
            logger.info("001 Starting get_card_label_infos method")

            if not self.cc.card_present:
                logger.info("002 No card present")
                return None

            response, sw1, sw2, label = self.cc.card_get_label()

            if label is None:
                logger.info("003 Label is None")
                return None

            if label == "":
                logger.info("004 Label is Blank")
                return ""

            logger.info(f"005 Label found: {label}")
            logger.log(SUCCESS, "006 Card label retrieved successfully")
            return label

        except CardError as e:
            logger.error(f"007 CardError in get_card_label_infos: {e}", exc_info=True)
            raise ControllerError(f"008 Failed to get card label: {e}") from e

        except Exception as e:
            logger.error(f"009 Unexpected error in get_card_label_infos: {e}", exc_info=True)
            raise ControllerError(f"010 Unexpected error while getting card label: {e}") from e

    ####################################################################################################################
    """MY SECRETS MANAGEMENT"""
    ####################################################################################################################
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
                'id': int(header['id']),  # Convertir l'ID en entier
                'type': dic_type.get(header['type'], hex(header['type'])),
                'label': header['label']
            }
            formatted_headers.append(formatted_header)

        return {
            'num_secrets': len(headers),
            'headers': formatted_headers
        }

    @log_method
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

        def process_secret(secret_type, secret_value):
            try:
                logger.info("001 Processing secret")
                if secret_type == 0x10:  # Masterseed
                    logger.info("002 Processing Masterseed")
                    return f"{secret_value}"
                elif secret_type in [0x30, 0x40]:  # BIP39 or Electrum mnemonicexit
                    logger.info("003 Processing mnemonic")
                    return f"{secret_value}"
                else:
                    logger.info("004 Processing other type of secret")
                    return f"{secret_value}"
            except Exception as e:
                logger.error(f"005 Error processing secret: {e}", exc_info=True)
                raise SecretProcessingError(f"006 Failed to process secret: {e}") from e

        try:
            logger.info(f"007 Retrieving details for secret ID: {secret_id}")
            secret_details = self.cc.seedkeeper_export_secret(secret_id)
            logger.debug("008 Secret details exported from card")

            processed_secret = process_secret(secret_details['type'], secret_details['secret'])

            formatted_details = {
                'label': secret_details['label'],
                'type': dic_type.get(secret_details['type'], hex(secret_details['type'])),
                'secret': processed_secret
            }

            logger.log(SUCCESS, f"009 Secret details retrieved and processed successfully")
            return formatted_details

        except SecretProcessingError as e:
            logger.error(f"010 Error processing secret: {e}", exc_info=True)
            raise SecretRetrievalError(f"011 Failed to process secret: {e}") from e
        except Exception as e:
            logger.error(f"012 Error retrieving secret details: {e}", exc_info=True)
            raise SecretRetrievalError(f"013 Failed to retrieve secret details: {e}") from e

    ####################################################################################################################
    """ GENERATE SECRETS """
    ####################################################################################################################
    @log_method
    def generate_random_seed(self, mnemonic_length):
        try:
            logger.info(f"001 Generating random seed of length {mnemonic_length}")
            strength = 128 if mnemonic_length == 12 else 256
            mnemonic = Mnemonic("english").generate(strength=strength)
            logger.log(SUCCESS, f"002 Random seed of length {mnemonic_length} generated successfully")
            return mnemonic
        except Exception as e:
            logger.error(f"003 Error generating random seed: {e}", exc_info=True)
            raise ControllerError(f"004 Failed to generate random seed: {e}")

    @log_method
    def import_seed(self, mnemonic, passphrase=None):
        try:
            logger.info("001 Importing seed")
            MNEMONIC = Mnemonic(language="english")
            if MNEMONIC.check(mnemonic):
                logger.info("002 Imported seed is valid")
                if passphrase:
                    seed = Mnemonic.to_seed(mnemonic, passphrase)
                else:
                    seed = Mnemonic.to_seed(mnemonic)
                self.card_setup_native_seed(seed)
                logger.log(SUCCESS, "003 Seed imported successfully")
            else:
                logger.warning("004 Imported seed is invalid")
                self.view.show('WARNING', "Invalid BIP39 seedphrase, please retry.", 'Ok', None,
                               "./pictures_db/generate_icon_ws.png")
        except Exception as e:
            logger.error(f"005 Error importing seed: {e}", exc_info=True)
            self.view.show("ERROR", "Failed to import seed", "Ok", None, "./pictures_db/generate_icon_ws.png")

    @log_method
    def card_setup_native_seed(self, seed):
        # get authentikey
        try:
            authentikey = self.cc.card_bip32_get_authentikey()
        except UninitializedSeedError:
            # seed dialog...
            authentikey = self.cc.card_bip32_import_seed(seed)
            logger.info(f"authentikey: {authentikey}")
            if authentikey:
                self.is_seeded = True
                self.view.show('SUCCESS',
                               'Your card is now seeded!',
                               'Ok',
                               lambda: None,
                               "./pictures_db/icon_seed_popup.jpg")
                self.view.update_status()
                self.view.view_start_setup()

                hex_authentikey = authentikey.get_public_key_hex()
                logger.info(f"Authentikey={hex_authentikey}")
            else:
                self.view.show('ERROR', 'Error when importing seed to Satochip!', 'Ok', None,
                               "./pictures_db/icon_seed_popup.jpg")

    import json

    def get_logs(self):
        logger.debug('In get_logs')
        ins_dic = {0x40: 'Create PIN', 0x42: 'Verify PIN', 0x44: 'Change PIN', 0x46: 'Unblock PIN',
                   0xA0: 'Generate masterseed', 0xA5: 'Reset secret', 0xAE: 'Generate 2FA Secret',
                   0xA1: 'Import secret', 0xA1A: 'Import plain secret', 0xA1B: 'Import encrypted secret',
                   0xA2: 'Export secret', 0xA2A: 'Export plain secret', 0xA2B: 'Export encrypted secret',
                   0xFF: 'RESET TO FACTORY'}
        res_dic = {0x9000: 'OK', 0x63C0: 'PIN failed', 0x9C03: 'Operation not allowed', 0x9C04: 'Setup not done',
                   0x9C05: 'Feature unsupported',
                   0x9C01: 'No memory left', 0x9C08: 'Secret not found', 0x9C10: 'Incorrect P1', 0x9C11: 'Incorrect P2',
                   0x9C0F: 'Invalid parameter',
                   0x9C0B: 'Invalid signature', 0x9C0C: 'Identity blocked', 0x9CFF: 'Internal error',
                   0x9C30: 'Lock error', 0x9C31: 'Export not allowed',
                   0x9C32: 'Import data too long', 0x9C33: 'Wrong MAC during import', 0x0000: 'Unexpected error'}

        logs, nbtotal_logs, nbavail_logs = self.cc.seedkeeper_print_logs()

        logs = logs[0:nbtotal_logs]
        json_logs = []
        # convert raw logs to readable data
        for log in logs:
            ins = log[0]
            id1 = log[1]
            id2 = log[2]
            result = log[3]
            if ins == 0xA1:  # encrypted or plain import? depends on value of id2
                ins = 0xA1A if (id2 == 0xFFFF) else 0xA1B
            elif ins == 0xA2:
                ins = 0xA2A if (id2 == 0xFFFF) else 0xA2B
            ins = ins_dic.get(ins, hex(log[0]))

            id1 = 'N/A' if id1 == 0xFFFF else str(id1)
            id2 = 'N/A' if id2 == 0xFFFF else str(id2)

            if (result & 0x63C0) == 0x63C0:  # last nible contains number of pin remaining
                remaining_tries = (result & 0x000F)
                result = f'PIN failed - {remaining_tries} tries remaining'
            else:
                result = res_dic.get(log[3], hex(log[3]))

            json_logs.append({
                "Operation": ins,
                "ID1": id1,
                "ID2": id2,
                "Result": result
            })

        # Convert to JSON string
        json_string = json.dumps(json_logs)
        logger.debug(f"JSON formatted logs: {json_string}")

        print(json_logs)
        print(nbtotal_logs)
        print(nbavail_logs)

        return nbtotal_logs, nbavail_logs, json_logs