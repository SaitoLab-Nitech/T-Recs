import io
import logging
import subprocess

logger = logging.getLogger(name=__name__)


class CommandRunner:
    """
    Run shell commands.
    """
    @staticmethod
    def run(cmd, timeout=None):
        """
        Run the given command.
        """
        logger.debug('running command')

        # cmd might contain sensitive information
        #logger.debug(f'{cmd = }')

        try:
            output = subprocess.check_output(cmd, timeout=timeout, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            raise Exception(f'{cmd = }\n'
                            f'{e.output.decode("utf-8") = }') from e
        except subprocess.TimeoutExpired as e:
            raise Exception(f'Timeout {cmd = }\n'
                            f'{e.output.decode("utf-8") = }') from e

        return output

    @staticmethod
    def start_process(cmd):
        """
        Run the given command and return the process.
        """
        logger.debug('starting process')

        try:
            return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            raise Exception(f'{cmd = }\n'
                            f'{e.output.decode("utf-8") = }') from e

    @staticmethod
    def start_process_with_redirecting_to_file(cmd, output_path):
        """
        Run the given command and return the process.

        :param output_path:    Path to log file.
        """
        logger.debug('starting process with redirecting to file')

        try:
            f = io.open(output_path, 'w', encoding='utf-8', errors='ignore')
            return subprocess.Popen(cmd, stdout=f, stderr=f)
        except subprocess.CalledProcessError as e:
            raise Exception(f'{cmd = }\n'
                            f'{e.output.decode("utf-8") = }') from e

# Failed with mitmdump and ts commands, so use shell=True instead
#     @staticmethod
#     def start_processes_with_pipe(cmd1, cmd2, output_path):
#         """
#         Run the given two commands with a pipe and return the process.
# 
#         :param output_path:    Path to log file.
#         """
#         logger.debug('starting processes with a pipe')
# 
#         try:
#             process1 = subprocess.Popen(cmd1, stdout=subprocess.PIPE)
# 
#             f = io.open(output_path, 'w', encoding='utf-8', errors='ignore')
#             process2 = subprocess.Popen(cmd2, stdin=process1.stdout, stdout=f, stderr=f)
# 
#             return process1, process2
#         except subprocess.CalledProcessError as e:
#             raise Exception(f'{cmd1 = }\n'
#                             f'{cmd2 = }\n'
#                             f'{e.output.decode("utf-8") = }') from e
