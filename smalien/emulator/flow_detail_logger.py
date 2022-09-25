import logging

from smalien.definitions import FLOW_DETAIL_LOG_FILE

class FlowDetailLogger:
    log_file = None

    @staticmethod
    def open_flow_detail_log_file(workspace):
        """
        Open flow detail log file in the given workspace.
        """
        FlowDetailLogger.log_file = open(workspace / FLOW_DETAIL_LOG_FILE, 'w')

    @staticmethod
    def write(string):
        """
        Write the given string to file.
        """
        FlowDetailLogger.log_file.write(string)
