import smalien
import sys
import logging


def run_automatic_exerciser():
    # Setup the log level
    logging.getLogger('smalien').setLevel('DEBUG')

    # Specify your devices
    DEVICES = [
        'emulator-5554',
        'emulator-5556',
    ]
    ACTION_NUM_LIMIT = 30

    # Create a project and get the exerciser
    project = smalien.Project(sys.argv[1])

    detected_leaks = project.exercise_automatically(DEVICES, ACTION_NUM_LIMIT)

    # Print result
    logging.warning(f'{detected_leaks = }')

if __name__ == '__main__':
    run_automatic_exerciser()
