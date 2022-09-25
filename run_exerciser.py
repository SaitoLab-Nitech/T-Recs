import smalien
import sys
import logging


def run_exerciser():
    # Setup the log level
    logging.getLogger('smalien').setLevel('DEBUG')

    # Specify your device
    # You can get a list of your device by 'adb devices'
    DEVICE = 'emulator-5554'

    exr = smalien.Project(sys.argv[1], device=DEVICE).exerciser

    # Start exercising the app
    exr.clear()

    exr.install(seconds=1)

    # Launch the app and wait for 60 seconds
    exr.launch()
    exr.sleep(60)

    exr.uninstall()

    exr.collect()

if __name__ == '__main__':
    run_exerciser()
