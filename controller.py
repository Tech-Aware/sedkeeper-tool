import sys
import os
from typing import Optional, Dict, List, Callable, Any
from functools import wraps
import logging
import json
import binascii
from mnemonic import Mnemonic
import hashlib

from pysatochip.CardConnector import (CardConnector, CardNotPresentError, PinRequiredError, WrongPinError,
                                                 PinBlockedError, UnexpectedSW12Error, CardSetupNotDoneError,
                                                 UninitializedSeedError, ApduError, SeedKeeperError,
)

from log_config import log_method
from exceptions import *

logger = get_logger(__name__)


class Controller:
    dic_type = {
        0x10: 'Masterseed',
        0x30: 'BIP39 mnemonic',
        0x40: 'Electrum mnemonic',
        0x50: 'Shamir Secret Share',
        0x60: 'Private Key',
        0x70: 'Public Key',
        0x71: 'Authenticated Public Key',
        0x80: 'Symmetric Key',
        0x90: 'Password',
        0x91: 'Master Password',
        0xA0: 'Certificate',
        0xB0: '2FA secret',
        0xC0: 'Free text',
        0xC1: 'Wallet descriptor'
    }


    @log_method
    def __init__(self, cc, view, loglevel=setup_logging()):
        self.view = view
        self.view.controller = self
        self.truststore={}

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
                                self.add_authentikey_to_truststore()
                            else:
                                self.card_setup_native_pin(pin)
                                self.add_authentikey_to_truststore()
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

        formatted_headers = []
        for header in headers:
            formatted_header = {
                'id': int(header['id']),  # Convertir l'ID en entier
                'type': Controller.dic_type.get(header['type'], hex(header['type'])),
                'subtype': Controller.dic_type.get(header['subtype'], hex(header['subtype'])),
                'origin': Controller.dic_type.get(header['origin'], hex(header['origin'])),
                'export_rights': Controller.dic_type.get(header['export_rights'], hex(header['export_rights'])),
                'label': header['label']
            }
            formatted_headers.append(formatted_header)

        logger.debug(f"Formated headers: {formatted_headers}")
        return {
            'num_secrets': len(headers),
            'headers': formatted_headers
        }

    @log_method
    def retrieve_details_about_secret_selected(self, secret_id):

        def process_secret(secret_type, secret_value):
            try:
                logger.info("Processing secret")
                for type in Controller.dic_type:
                    if type == secret_type:
                        return f"{secret_value}"
            except Exception as e:
                logger.error(f"Error processing secret: {e}", exc_info=True)
                raise SecretProcessingError(f"006 Failed to process secret: {e}") from e

        try:
            logger.info(f"Retrieving details for secret ID: {secret_id}")
            secret_details = self.cc.seedkeeper_export_secret(secret_id)
            logger.debug(f"secret details: {secret_details}")
            logger.debug("Secret details exported from card")

            processed_secret = process_secret(secret_details['type'], secret_details['secret'])
            logger.info(f"Processed secret: {processed_secret}")

            formatted_details = {
                'label': secret_details['label'],
                'type': Controller.dic_type.get(secret_details['type'], hex(secret_details['type'])),
                'subtype': secret_details['subtype'],
                'export_rights': hex(secret_details['export_rights']),
                'secret': processed_secret
            }

            logger.log(SUCCESS, f"Secret details retrieved and processed successfully: {formatted_details}")
            return formatted_details

        except SecretProcessingError as e:
            logger.error(f"Error processing secret: {e}", exc_info=True)
            raise SecretRetrievalError(f"Failed to process secret: {e}") from e
        except Exception as e:
            logger.error(f"Error retrieving secret details: {e}", exc_info=True)
            raise SecretRetrievalError(f"Failed to retrieve secret details: {e}") from e

    ####################################################################################################################
    """ GENERATE SECRETS """
    ####################################################################################################################
    @log_method
    def generate_random_seed(self, mnemonic_length):
        try:
            logger.info(f"Generating random seed of length {mnemonic_length}")
            strength = 128 if mnemonic_length == 12 else 256
            mnemonic = Mnemonic("english").generate(strength=strength)
            logger.log(SUCCESS, f"Random seed of length {mnemonic_length} generated successfully")
            return mnemonic
        except Exception as e:
            logger.error(f"Error generating random seed: {e}", exc_info=True)
            raise ControllerError(f"Failed to generate random seed: {e}")

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

        logger.debug(json_logs)
        logger.debug(nbtotal_logs)
        logger.debug(nbavail_logs)

        return nbtotal_logs, nbavail_logs, json_logs

    @log_method
    def import_password(self, label: str, login: str, password: str, url: str = None):
        try:
            logger.info("Starting password import process")

            # Préparer les données pour l'importation
            secret_type = 0x90  # Type pour mot de passe
            export_rights = 0x01  # Droits d'exportation (à ajuster selon vos besoins)

            # Créer le dictionnaire secret
            secret_dic = {
                'header': self.cc.make_header(secret_type, export_rights, label),
                'secret_list': list(password.encode('utf-8'))
            }

            # Ajouter des métadonnées supplémentaires
            metadata = f"login:{login}\nurl:{url}"
            secret_dic['secret_list'] += list(metadata.encode('utf-8'))

            # Appeler la méthode d'importation de secret
            id, fingerprint = self.cc.seedkeeper_import_secret(secret_dic)

            logger.log(SUCCESS, f"Password imported successfully with id: {id} and fingerprint: {fingerprint}")

            return id, fingerprint

        except SeedKeeperError as e:
            logger.error(f"SeedKeeper error during password import: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during password import: {str(e)}")
            raise ControllerError(f"Failed to import password: {str(e)}") from e

    @log_method
    def import_masterseed(self, label: str, mnemonic: str, passphrase: Optional[str] = None):
        try:
            logger.info("001 Starting masterseed import process")

            # Validate the mnemonic
            mnemonic = mnemonic.strip()
            word_count = len(mnemonic.split())
            if word_count not in [12, 24]:
                raise ValueError(f"002 Invalid mnemonic word count: {word_count}. Must be 12 or 24.")

            # Verify mnemonic validity
            MNEMONIC = Mnemonic("english")
            if not MNEMONIC.check(mnemonic):
                raise ValueError("003 Invalid mnemonic")

            # Generate entropy from mnemonic
            entropy = MNEMONIC.to_entropy(mnemonic)

            # Generate seed
            salt = "mnemonic" + (passphrase or "")
            seed = hashlib.pbkdf2_hmac("sha512", mnemonic.encode("utf-8"), salt.encode("utf-8"), 2048)

            # Prepare the secret data
            wordlist_selector = 0x00  # english
            entropy_list = list(entropy)
            seed_list = list(seed)
            passphrase_list = list(passphrase.encode('utf-8')) if passphrase else []

            secret_list = (
                    [len(seed_list)] +
                    seed_list +
                    [wordlist_selector] +
                    [len(entropy_list)] +
                    entropy_list +
                    [len(passphrase_list)] +
                    passphrase_list
            )

            # Prepare the header
            secret_type = 0x10  # SECRET_TYPE_MASTER_SEED
            export_rights = 0x01  # SECRET_EXPORT_ALLOWED
            subtype = 0x01  # SECRET_SUBTYPE_BIP39

            secret_dic = {
                'header': self.cc.make_header(secret_type, export_rights, label, subtype=subtype),
                'secret_list': secret_list
            }

            # Import the secret
            id, fingerprint = self.cc.seedkeeper_import_secret(secret_dic)

            logger.log(SUCCESS, f"004 Masterseed imported successfully with id: {id} and fingerprint: {fingerprint}")
            return id, fingerprint

        except ValueError as e:
            logger.error(f"005 Validation error during masterseed import: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"006 Unexpected error during masterseed import: {str(e)}")
            raise ControllerError(f"007 Failed to import masterseed: {str(e)}") from e

    @log_method
    def import_free_text(self, label: str, free_text: str):
        try:
            logger.info("Starting import of free text")

            # Validate input
            if not label:
                raise ValueError("Label is required")
            if not free_text:
                raise ValueError("Free text is required")

            # Prepare the secret data
            secret_type = 0xC0  # SECRET_TYPE_FREE_TEXT
            secret_subtype = 0x00  # SECRET_SUBTYPE_DEFAULT
            export_rights = 0x01  # SECRET_EXPORT_ALLOWED

            # Encode the free text
            raw_text_bytes = free_text.encode('utf-8')
            text_size = len(raw_text_bytes)

            # Prepare the secret dictionary
            secret_dic = {
                'header': self.cc.make_header(secret_type, export_rights, label, subtype=secret_subtype),
                'secret_list': list(text_size.to_bytes(2, byteorder='big')) + list(raw_text_bytes)
            }

            # Import the secret
            id, fingerprint = self.cc.seedkeeper_import_secret(secret_dic)

            logger.log(SUCCESS, f"Free text imported successfully with id: {id} and fingerprint: {fingerprint}")
            return id, fingerprint

        except ValueError as e:
            logger.error(f"Validation error during free text import: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during free text import: {str(e)}")
            raise ControllerError(f"Failed to import free text: {str(e)}") from e

    @log_method
    def import_wallet_descriptor(self, label: str, wallet_descriptor: str):
        try:
            logger.info("Starting import of wallet descriptor")

            # Validate input
            if not label:
                raise ValueError("Label is required")
            if not wallet_descriptor:
                raise ValueError("Wallet descriptor is required")

            # Prepare the secret data
            secret_type = 0xC1  # SECRET_TYPE_WALLET_DESCRIPTOR
            secret_subtype = 0x00  # SECRET_SUBTYPE_DEFAULT
            export_rights = 0x01  # SECRET_EXPORT_ALLOWED

            # Encode the wallet descriptor
            raw_descriptor_bytes = wallet_descriptor.encode('utf-8')
            descriptor_size = len(raw_descriptor_bytes)

            if descriptor_size > 65535:  # 2^16 - 1, max value for 2 bytes
                raise ValueError("Wallet descriptor is too long (max 65535 bytes)")

            # Prepare the secret dictionary
            secret_dic = {
                'header': self.cc.make_header(secret_type, export_rights, label, subtype=secret_subtype),
                'secret_list': list(descriptor_size.to_bytes(2, byteorder='big')) + list(raw_descriptor_bytes)
            }

            # Import the secret
            id, fingerprint = self.cc.seedkeeper_import_secret(secret_dic)

            logger.log(SUCCESS, f"Wallet descriptor imported successfully with id: {id} and fingerprint: {fingerprint}")
            return id, fingerprint

        except ValueError as e:
            logger.error(f"Validation error during wallet descriptor import: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during wallet descriptor import: {str(e)}")
            raise ControllerError(f"Failed to import wallet descriptor: {str(e)}") from e

    @log_method
    def decode_secret(self, secret_dict: Dict[str, Any]) -> Dict[str, Any]:
        try:
            logger.info("Starting secret decoding process")
            logger.debug(f"Secret dictionary provided: {secret_dict}")

            # Mapping des types de secrets
            secret_type_mapping = {
                "Masterseed": 0x10,
                "BIP39 mnemonic": 0x30,
                "Electrum mnemonic": 0x40,
                "Password": 0x90
            }

            result = {
                'type': secret_type_mapping.get(secret_dict['type']),
                'subtype': secret_dict.get('subtype', 0x00),  # Default subtype if not provided
            }

            if result['type'] is None:
                raise ValueError(f"Unsupported secret type: {secret_dict['type']}")

            logger.debug(f"Initial result dictionary: {result}")

            # Convertir la chaîne hexadécimale du secret en bytes
            try:
                secret_bytes = binascii.unhexlify(secret_dict['secret'])
                logger.debug(f"Secret bytes: {secret_bytes.hex()}")
            except binascii.Error:
                raise ValueError("Invalid hexadecimal string provided for secret")

            if result['type'] in [0x10, 0x30, 0x40]:  # Masterseed, BIP39, or Electrum mnemonic
                return self.decode_masterseed(result, secret_bytes)
            elif result['type'] == 0x90:  # Password
                return self._decode_password(result, secret_bytes)
            else:
                raise ValueError(f"Decoding not implemented for type: {hex(result['type'])}")

        except ValueError as e:
            logger.error(f"Validation error during secret decoding: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during secret decoding: {str(e)}")
            raise ControllerError(f"Failed to decode secret: {str(e)}") from e

    @log_method
    def _decode_password(self, result: Dict[str, Any], secret_bytes: bytes) -> Dict[str, Any]:
        try:
            logger.info("Decoding password secret")

            # Initialiser les champs
            result['password'] = ''
            result['login'] = ''
            result['url'] = ''

            # Décoder le contenu complet en UTF-8
            full_content = secret_bytes.decode('utf-8')
            logger.debug(f"Full decoded content: {full_content}")

            # Séparer les parties
            parts = full_content.split('login:')

            if len(parts) > 1:
                # Le mot de passe est la première partie
                result['password'] = parts[0].strip()

                # Traiter le reste
                remaining = parts[1]
                login_url_parts = remaining.split('url:')

                if len(login_url_parts) > 1:
                    result['login'] = login_url_parts[0].strip()
                    result['url'] = login_url_parts[1].strip()
                else:
                    result['login'] = remaining.strip()
            else:
                # Si 'login:' n'est pas trouvé, tout est considéré comme mot de passe
                result['password'] = full_content.strip()

            # Remplacer 'None' par une chaîne vide
            for key in result:
                if result[key] == 'None':
                    result[key] = ''

            logger.debug(f"Decoded password secret: {result}")
            return result
        except Exception as e:
            logger.error(f"Error decoding password secret: {str(e)}")
            raise ValueError(f"Failed to decode password secret: {str(e)}") from e

    @log_method
    def decode_masterseed(self, secret_dict: Dict[str, Any]) -> Dict[str, Any]:
        try:
            logger.info("Starting masterseed decoding process")
            logger.debug(f"Secret dictionary provided: {secret_dict}")

            # Mapping des types de secrets de chaîne à valeur hexadécimale
            secret_type_mapping = {
                "Masterseed": 0x10,
                "BIP39 mnemonic": 0x30,
                "Electrum mnemonic": 0x40
            }

            result = {
                'type': secret_type_mapping.get(secret_dict['type']),
                'subtype': secret_dict.get('subtype', 0x00),  # Default subtype if not provided
                'masterseed': b'',
                'mnemonic': '',
                'passphrase': '',
                'entropy': b'',
                'wordlist_selector': None
            }

            if result['type'] is None:
                raise ValueError(f"Unsupported secret type: {secret_dict['type']}")

            logger.debug(f"Initial result dictionary: {result}")

            # Convertir la chaîne hexadécimale du secret en bytes
            try:
                logger.debug(f"Secret_dict['secret'] before secret_bytes: {secret_dict['secret']}")
                secret_bytes = binascii.unhexlify(secret_dict['secret'])
                logger.debug(f"Secret bytes: {(secret_bytes)}")
            except binascii.Error:
                raise ValueError("Invalid hexadecimal string provided for secret")

            offset = 0

            if result['type'] == 0x10:  # SECRET_TYPE_MASTER_SEED
                logger.debug(f"Decoding SECRET_TYPE_MASTER_SEED with subtype: {hex(result['subtype'])}")

                if result['subtype'] in [0x00, 0x01]:  # DEFAULT or BIP39
                    logger.debug(f"Subtype is default or BIP39: {hex(result['subtype'])}")
                    masterseed_size = secret_bytes[offset]
                    offset += 1
                    result['masterseed'] = secret_bytes[offset:offset + masterseed_size]

                    if result['subtype'] == 0x00: #default masterseed:
                        result['mnemonic'] = secret_bytes[offset:].hex()


                    logger.debug(f"The masterseed: {result['masterseed']} had been store into result_dict['masterseed']")
                    offset += masterseed_size


                    if result['subtype'] == 0x01:  # BIP39
                        result['wordlist_selector'] = secret_bytes[offset]
                        offset += 1

                        entropy_size = secret_bytes[offset]
                        offset += 1
                        result['entropy'] = secret_bytes[offset:offset + entropy_size]
                        offset += entropy_size

                        # Génération de la mnemonic à partir de l'entropie
                        # Mnemonic generation from entripy
                        if result['entropy']:
                            mnemonic_instance = Mnemonic("english")  # Utiliser le sélecteur de liste pour d'autres langues si nécessaire
                            result['mnemonic'] = mnemonic_instance.to_mnemonic(result['entropy'])
                            result['masterseed'] = secret_bytes[1:offset - (entropy_size + 2)].hex()
                            logger.debug(f"Generated Mnemonic: {result['mnemonic']} {result['masterseed']}")

                        logger.debug(f"secret_bytes length: {len(secret_bytes)}")
                        logger.debug(f"offset value: {offset}")
                        logger.debug(f"secret_bytes content: {secret_bytes.hex()}")

                        passphrase_size = secret_bytes[offset]
                        offset += 1
                        if passphrase_size > 0:
                            result['passphrase'] = secret_bytes[offset:offset + passphrase_size].decode('utf-8')
                else:
                    raise ValueError(f"Unknown subtype for SECRET_TYPE_MASTER_SEED: {hex(result['subtype'])}")

            elif result['type'] in [0x30, 0x40]:  # SECRET_TYPE_BIP39_MNEMONIC or SECRET_TYPE_ELECTRUM_MNEMONIC
                logger.debug(f"Decoding {'BIP39_MNEMONIC' if result['type'] == 0x30 else 'ELECTRUM_MNEMONIC'}")

                if result['subtype'] == 0x00:  # SECRET_SUBTYPE_DEFAULT
                    mnemonic_size = secret_bytes[offset]
                    offset += 1
                    result['mnemonic'] = secret_bytes[offset:offset + mnemonic_size]
                    offset += mnemonic_size

                    passphrase_size = secret_bytes[offset] if offset < len(secret_bytes) else 0
                    offset += 1
                    if passphrase_size > 0 and offset < len(secret_bytes):
                        result['passphrase'] = secret_bytes[offset:offset + passphrase_size]
                else:
                    raise ValueError(f"Unknown subtype for BIP39/ELECTRUM_MNEMONIC: {hex(result['subtype'])}")

            else:
                raise ValueError(f"Unsupported secret type for masterseed: {hex(result['type'])}")

            # Vérification de la mnémonique
            if result['mnemonic']:
                mnemonic = result['mnemonic']
                mnemonic_instance = Mnemonic("english")  # Nous supposons l'anglais par défaut
                if not mnemonic_instance.check(mnemonic):
                    logger.debug(f"Maybe mnemonic: {mnemonic} is electrum only")

            logger.info("Masterseed successfully decoded")
            logger.debug(f"Decoded: {result}")
            return result

        except ValueError as e:
            logger.error(f"Validation error during masterseed decoding: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during masterseed decoding: {str(e)}")
            raise ControllerError(f"Failed to decode masterseed: {str(e)}") from e

    @log_method
    def decode_free_text(self, secret_dict: Dict[str, Any]) -> Dict[str, Any]:
        try:
            logger.info("Starting free text decoding process")
            logger.debug(f"Secret dictionary provided: {secret_dict}")

            result = {
                'type': secret_dict['type'],
                'label': secret_dict['label'],
                'text': ''
            }

            # Convert the hexadecimal string of the secret to bytes
            try:
                secret_bytes = binascii.unhexlify(secret_dict['secret'])
                logger.debug(f"Secret bytes: {secret_bytes.hex()}")
            except binascii.Error:
                raise ValueError("Invalid hexadecimal string provided for secret")

            # Extract the text size (first 2 bytes)
            if len(secret_bytes) < 2:
                raise ValueError("Secret is too short to contain size information")
            text_size = int.from_bytes(secret_bytes[:2], byteorder='big')
            logger.debug(f"Decoded text size: {text_size}")

            # Extract and decode the raw text bytes
            raw_text_bytes = secret_bytes[2:]
            if len(raw_text_bytes) != text_size:
                raise ValueError(
                    f"Mismatch between declared text size ({text_size}) and actual data size ({len(raw_text_bytes)})")

            try:
                decoded_text = raw_text_bytes.decode('utf-8')
                result['text'] = decoded_text
                logger.debug(f"Decoded text: {decoded_text}")
            except UnicodeDecodeError:
                raise ValueError("Failed to decode text as UTF-8")

            logger.log(SUCCESS, "Free text successfully decoded")
            return result

        except ValueError as e:
            logger.error(f"Validation error during free text decoding: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during free text decoding: {str(e)}")
            raise ControllerError(f"Failed to decode free text: {str(e)}") from e

    @log_method
    def decode_wallet_descriptor(self, secret_dict: Dict[str, Any]) -> Dict[str, Any]:
        try:
            logger.info("Starting wallet descriptor decoding process")
            logger.debug(f"Secret dictionary provided: {secret_dict}")

            result = {
                'type': secret_dict['type'],
                'label': secret_dict['label'],
                'descriptor': ''
            }

            # Convert the hexadecimal string of the secret to bytes
            try:
                secret_bytes = binascii.unhexlify(secret_dict['secret'])
                logger.debug(f"Secret bytes: {secret_bytes.hex()}")
            except binascii.Error:
                raise ValueError("Invalid hexadecimal string provided for secret")

            # Extract the descriptor size (first 2 bytes)
            if len(secret_bytes) < 2:
                raise ValueError("Secret is too short to contain size information")
            descriptor_size = int.from_bytes(secret_bytes[:2], byteorder='big')
            logger.debug(f"Decoded descriptor size: {descriptor_size}")

            # Extract and decode the raw descriptor bytes
            raw_descriptor_bytes = secret_bytes[2:]
            if len(raw_descriptor_bytes) != descriptor_size:
                raise ValueError(
                    f"Mismatch between declared descriptor size ({descriptor_size}) and actual data size ({len(raw_descriptor_bytes)})")

            try:
                decoded_descriptor = raw_descriptor_bytes.decode('utf-8')
                result['descriptor'] = decoded_descriptor
                logger.debug(f"Decoded descriptor: {decoded_descriptor}")
            except UnicodeDecodeError:
                raise ValueError("Failed to decode descriptor as UTF-8")

            logger.log(SUCCESS, "Wallet descriptor successfully decoded")
            return result

        except ValueError as e:
            logger.error(f"Validation error during wallet descriptor decoding: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during wallet descriptor decoding: {str(e)}")
            raise ControllerError(f"Failed to decode wallet descriptor: {str(e)}") from e

    def add_authentikey_to_truststore(self):
        logger.debug('In add_authentikey_to_truststore()')

        # Vérifier si la carte est présente
        if not self.cc.card_present:
            logger.warning("No card present, unable to add authentikey.")
            return False

        # Exporter l'authentikey
        try:
            self.authentikey = self.cc.card_export_authentikey()
        except Exception as ex:
            logger.warning(f"Failed to export authentikey: {repr(ex)}")
            self.view.show('ERROR', repr(ex), 'Ok', None)
            return False

        # Récupérer le label de la carte
        try:
            (response, sw1, sw2, card_label) = self.cc.card_get_label()
            self.card_label = card_label
        except Exception as ex:
            logger.warning(f"Error while getting card label: {str(ex)}")

        # Ajouter l'authentikey à la TrustStore
        authentikey_hex = self.authentikey.get_public_key_bytes(compressed=False).hex()

        if authentikey_hex in self.truststore:
            logger.info('Authentikey already in TrustStore!')
            self.view.show('INFOS', 'Authentikey already in TrustStore!', 'Ok', None)
        else:
            # Si l'authentikey n'est pas encore présente dans le TrustStore
            authentikey_bytes = bytes.fromhex(authentikey_hex)
            secret = bytes([len(authentikey_bytes)]) + authentikey_bytes
            fingerprint = hashlib.sha256(secret).hexdigest()[0:8]  # Empreinte SHA-256
            authentikey_comp = self.authentikey.get_public_key_bytes(compressed=True).hex()  # Clé publique compressée

            # Ajouter l'authentikey à la TrustStore avec le label et l'empreinte
            self.truststore[authentikey_hex] = {
                'card_label': self.card_label,
                'fingerprint': fingerprint,
                'authentikey_comp': authentikey_comp
            }
            print(self.truststore)

            logger.info('Authentikey added to TrustStore!')
            self.view.show('INFOS:', f'Authentikey added to TrustStore! \n{authentikey_comp}', 'Ok', None)

        return True

    def get_secret_header_list(self):
        # get a list of all the secrets & pubkeys available
        # dic_type= {0x30:'BIP39 mnemonic', 0x40:'Electrum mnemonic', 0x10:'Masterseed', 0x70:'Public Key', 0x90:'Password'}
        label_list = []
        id_list = []
        label_pubkey_list = ['None (export to plaintext)']
        id_pubkey_list = [None]
        fingerprint_pubkey_list = []
        try:
            headers = self.cc.seedkeeper_list_secret_headers()
            for header_dic in headers:
                label_list.append(Controller.dic_type.get(header_dic['type'], hex(header_dic['type'])) + ': ' + header_dic[
                    'fingerprint'] + ': ' + header_dic['label'])
                id_list.append(header_dic['id'])
                if header_dic['type'] == 0x70:
                    pubkey_dic = self.cc.seedkeeper_export_secret(header_dic['id'],
                                                                  None)  # export pubkey in plain #todo: compressed form?
                    pubkey = pubkey_dic['secret'][2:10]  # [0:2] is the pubkey size in hex
                    label_pubkey_list.append('In SeedKeeper: ' + header_dic['fingerprint'] + ': ' + header_dic[
                        'label'] + ': ' + pubkey + '...')
                    id_pubkey_list.append(header_dic['id'])
                    fingerprint_pubkey_list.append(header_dic['fingerprint'])
        except Exception as ex:
            logger.error(f"Error during secret header listing: {ex}")
            # self.show_error(f'Error during secret export: {ex}')
            # return None

        # add authentikeys from Truststore
        label_authentikey_list, authentikey_list = self.get_truststore_list(fingerprint_pubkey_list)
        label_pubkey_list.extend(label_authentikey_list)
        id_pubkey_list.extend(authentikey_list)

        return label_list, id_list, label_pubkey_list, id_pubkey_list

    def get_truststore_list(self, fingerprint_list=[]):
        # get list of authentikeys from TrustStore, whose fingerprint is not already in fingerprint_list
        label_authentikey_list = []
        authentikey_list = []
        for authentikey, dic_info in self.truststore.items():
            if authentikey == self.cc.parser.authentikey.get_public_key_bytes(
                    False).hex():  # self.authentikey.get_public_key_bytes(False).hex():
                continue  # skip own authentikey
            card_label = dic_info['card_label']
            fingerprint = dic_info['fingerprint']
            authentikey_comp = dic_info['authentikey_comp']
            if fingerprint not in fingerprint_list:  # skip authentikey already in device
                keyvalue = 'In Truststore: ' + fingerprint + ': ' + card_label + ' authentikey' + ": " + authentikey_comp[
                                                                                                         0:8] + "..."
                label_authentikey_list.append(keyvalue)
                authentikey_list.append(authentikey)

        return label_authentikey_list, authentikey_list