import logging


logger = logging.getLogger(name=__name__)


class Action:
    """
    Base class of *Action classes.
    """

    def __init__(self, target, exerciser):
        self.target = target
        self.exerciser = exerciser

    def get(self):
        """
        Returns the run method.
        """

        return self.run

    def run(self):
        """
        Perform an action.
        This method will be overridden by the child class.
        """
        pass

class ServiceAction(Action):
    """
    Action to start the given service.
    """

    def run(self):
        logger.debug(f'running service action {self.target = }')

        try:
            self.exerciser.start_service(self.target)
        except Exception as e:
            logger.debug(f'service action failed {e = }')

class ReceiverAction(Action):
    """
    Action to start the given receiver.
    """

    def run(self):
        logger.debug(f'running receiver action {self.target = }')

        try:
            self.exerciser.send_broadcast(self.target)
        except Exception as e:
            logger.debug(f'receiver action failed {e = }')

class ActivityAction(Action):
    """
    Action to start the given activity.
    """

    def run(self):
        logger.debug(f'running activity action {self.target = }')

        try:
            self.exerciser.start_activity(self.target)
        except Exception as e:
            logger.debug(f'activity action failed {e = }')

class TapAction(Action):
    """
    Action to tap the given list of [x, y] coordinates of screen.
    """

    def run(self):
        logger.debug(f'running tap action {self.target = }')

        try:
            for coord in self.target:
                self.exerciser.tap_screen(coord[0], coord[1], seconds=7)
        except Exception as e:
            logger.debug(f'tap action failed {e = }')

class LaunchTapAction(Action):
    """
    Action to launch the app and tap the given list of [x, y] coordinates of screen.
    """

    def run(self):
        logger.debug(f'running launch and tap action {self.target = }')

        try:
            self.exerciser.launch(seconds=2)

            for coord in self.target:
                self.exerciser.tap_screen(coord[0], coord[1], seconds=7)
        except Exception as e:
            logger.debug(f'tap action failed {e = }')
