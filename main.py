import sys

if sys.version_info <= (3, 5):
    print("Error: Please run with python3")
    sys.exit(1)

import logging
import os
import threading
import time

from PIL import Image

import debug
from data import Data
from data.config import Config
from renderers.main import MainRenderer
from utils import args, led_matrix_options

try:
    from rgbmatrix import RGBMatrix, __version__

    emulated = False
except ImportError:
    from RGBMatrixEmulator import RGBMatrix, version

    emulated = True


SCRIPT_NAME = "MTA Board"
SCRIPT_VERSION = "0.1.0"


def main(matrix, config_base):

    # Read scoreboard options from config.json if it exists
    config = Config(config_base, matrix.width, matrix.height)
    logger = logging.getLogger("mta-board")
    if config.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.WARNING)

    # Print some basic info on startup
    debug.info("%s - v%s (%sx%s)", SCRIPT_NAME, SCRIPT_VERSION, matrix.width, matrix.height)

    if emulated:
        debug.log("rgbmatrix not installed, falling back to emulator!")
        debug.log("Using RGBMatrixEmulator version %s", version.__version__)
    else:
        debug.log("Using rgbmatrix version %s", __version__)

    # Draw startup screen
    logo_path = os.path.abspath("./assets/startup-w" + str(matrix.width) + "h" + str(matrix.height) + ".png")

    # see: https://github.com/ty-porter/RGBMatrixEmulator/issues/9#issuecomment-922869679
    if os.path.exists(logo_path) and not emulated:
        logo = Image.open(logo_path)
        matrix.SetImage(logo.convert("RGB"))
        logo.close()

    # Create a new data object to manage the MLB data
    # This will fetch initial data from MLB
    data = Data(config)

    # create render thread
    render = threading.Thread(target=__render_main, args=[matrix, data], name="render_thread", daemon=True)
    time.sleep(1)
    render.start()

    __refresh_data(render, data)


def __refresh_data(render_thread, data):  # type: (threading.Thread, Data) -> None
    while render_thread.is_alive():
        time.sleep(5)
        data.refresh_weather()
        data.refresh_arrivals()


def __render_main(matrix, data):
    MainRenderer(matrix, data).render()


if __name__ == "__main__":
    # Check for led configuration arguments
    command_line_args = args()
    matrixOptions = led_matrix_options(command_line_args)

    # Initialize the matrix
    matrix = RGBMatrix(options=matrixOptions)
    try:
        config, _ = os.path.splitext(command_line_args.config)
        main(matrix, config)
    except:
        debug.exception("Untrapped error in main!")
    finally:
        matrix.Clear()
        sys.exit(1)
