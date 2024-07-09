import subprocess
import os
import sys
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_pyinstaller():
    try:
        pyinstaller_path = os.path.join(sys.prefix, 'Scripts', 'pyinstaller.exe')
        if not os.path.isfile(pyinstaller_path):
            raise FileNotFoundError(f"PyInstaller non trouvé : {pyinstaller_path}")

        command = [
            pyinstaller_path,
            "--onefile",
            "--name", "seedkeeper_tool.exe",
            "--add-data", "pictures_db/*;pictures_db",
            # Retirez l'option --windowed pour permettre l'affichage de la console
            "--console",
            "seedkeeper_tool.py"
        ]

        logger.info("Démarrage du build Windows...")
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        logger.info("Build Windows terminé avec succès.")
        logger.debug(f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    except FileNotFoundError as e:
        logger.error(f"Erreur : {e}")
        logger.info("Assurez-vous que PyInstaller est installé et accessible dans le chemin système.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Erreur lors de l'exécution de PyInstaller : {e}")
        logger.debug(f"STDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}")
    except Exception as e:
        logger.error(f"Erreur inattendue lors du build Windows : {e}")
        raise

if __name__ == "__main__":
    run_pyinstaller()