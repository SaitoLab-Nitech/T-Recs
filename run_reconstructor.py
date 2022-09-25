import smalien
import sys
import logging


def run_emulator():
    # Setup the log level
    logging.getLogger('smalien').setLevel('DEBUG')    # Print information for debugging
    # logging.getLogger('smalien').setLevel('ERROR')  # Print little information

    project = smalien.Project(sys.argv[1])

    project.emulate_with_runtime_logs()

    # Print result
    logging.warning(f'{project.emulator.get_num_leaks() = }')

if __name__ == '__main__':
    run_emulator()
