import logging
from collections import defaultdict

from .exerciser import Exerciser
from ..emulator.emulator import Emulator
from .actions import ServiceAction, ReceiverAction, ActivityAction, TapAction, LaunchTapAction

logger = logging.getLogger(name=__name__)


class AutomaticExerciser():
    """
    Automatically exercise the app.
    """

    def __init__(self, app, workspace, taint_sources, taint_sinks, devices, action_num_limit=None):
        """
        
        :param action_num_limi:  The exerciser tries actions no more than <action_num_limit> times on each device.
        """

        logger.debug('initializing')

        # Parameters
        self.app = app
        self.workspace = workspace
        self.taint_sources = taint_sources
        self.taint_sinks = taint_sinks
        self.devices = devices
        self.action_num_limit = action_num_limit

        # Helper modules
        self.emulator = None
        self.exerciser = None

        # Initialize flow-causing actions
        self.flow_causing_actions = []

        # Keep results
        self.leak_detected_emulators = []

        # Calculate number of potential leaks
        self.num_potential_leaks = self.app.num_potential_sources * self.app.num_potential_sinks
        logger.debug(f'{self.num_potential_leaks = }')

    def run(self):
        """
        Start the automatic exerciser.
        """
        logger.debug('running')
        logger.debug(f'{self.devices = }')

        num_leaks_sum = 0

        for device in self.devices:
            logger.warning(f'automatically exercising {self.app.apk = } on {device = }')
            # Initialize
            self.flow_causing_actions = []

            self.exerciser = Exerciser(self.app, self.workspace, device)

            # Install the app
            # Make sure that the app is not installed
            try:
                self.exerciser.uninstall()
            except:
                pass

            self.exerciser.install(seconds=1)

            # Start exercising
            num_leaks_sum = self.exercise_and_emulate()

            # Uninstall the app
            self.exerciser.uninstall()

            # Finish the exercising if one or more leak is detected
            if (num_leaks_sum > 0):
                logger.debug('leak is detected, and exiting the automatic exerciser')
                break

        # Count and return the number of unique leaks
        return self.count_unique_leaks()

    def count_unique_leaks(self):
        """
        Count and return the number of unique leaks.
        """
        logger.debug('counting the number of unique leaks.')

        unique_leaks = defaultdict(set)

        for emulator in self.leak_detected_emulators:
            emulator.append_unique_leaks(unique_leaks)

        return sum([ len(sources) for sources in unique_leaks.values() ])

    def exercise_and_emulate(self):
        """
        Main algorithm of automatic exercising.
        """
        logger.debug('exercising')

        # Initialize information of detected leaks
        num_leaks_sum = 0
        leak_taint_histories = []
        prev_taint_history_size = 0

        # Initialize information of performed actions
        num_actions = 0

        # Start outer loop
        while True:

            # Clean the device, perform flow-causing actions, and obtain actionables
            self.clean()
            self.perform_flow_causing_actions()

            actionables = self.obtain_actionables()
            logger.debug(f'{actionables = }')

            # Start inner loop
            while actionables:

                # Finish if #actions reached to the action_num_limit
                if (self.action_num_limit is not None and num_actions >= self.action_num_limit):
                    logger.debug('the number of action reached to the limit')

                    return num_leaks_sum

                logger.debug(f'trying one of {len(actionables)} actionables')

                # Clean the device and perform flow-causing actions
                self.clean()
                self.perform_flow_causing_actions()

                # Pop and perform one of actionables.
                action = actionables.pop(0)
                action()

                # Count performed actions
                num_actions += len(self.flow_causing_actions) + 1
                logger.debug(f'{num_actions = }')

                # Sleep and collect SmalienLog
                self.exerciser.sleep(2)
                collected = self.exerciser.collect()

                # Apply information flow analysis to the app's executed code
                if (collected):
                    # Create an Emulator instance and perform information flow analysis.
                    logger.debug('app code is executed, and performing information flow analysis')

                    # Run the emulator
                    self.emulator = Emulator(self.app, self.workspace, self.taint_sources, self.taint_sinks)
                    try:
                        self.emulator.run_with_runtime_logs()
                    except:
                        # Ignore errors in emulator
                        pass

                    num_leaks = self.emulator.get_num_leaks()
                    taint_history_size = len(self.emulator.get_taint_history())
                    logger.debug(f'{num_leaks = }')
                    logger.debug(f'{taint_history_size = }')

                    if (num_leaks > 0):
                        logger.debug('leak is detected')

                        # Compare found flow to previously-found flows
                        matched = self.compare_found_flow(leak_taint_histories)
                        if (not matched):
                            # Count found flow
                            num_leaks_sum += num_leaks
                            leak_taint_histories.append(self.emulator.get_taint_history())

                            logger.critical(f'new leak is detected {num_leaks_sum = }')
                            logger.critical(f'performed total {num_actions = }')

                            # Save the leak-detected emulator
                            self.leak_detected_emulators.append(self.emulator)

                            # Check if num_leaks_sum reached num_potential_leaks
                            if (num_leaks_sum >= self.num_potential_leaks):
                                # Exit the inner and outer loops
                                logger.critical('#detected reached #potential_leaks')
                                return num_leaks_sum

                            else:
                                # Clear information of taint history and flow-causing actions, and break the inner loop
                                prev_taint_history_size = 0
                                self.flow_causing_actions = []

                                break

                    # Branch depending on the size of taint_history.
                    # If new flow is detected, add the action to flow-causing actions, and break the inner loop
                    if (prev_taint_history_size < taint_history_size):
                        logger.debug('new information flow is detected')

                        self.flow_causing_actions.append(action)

                        break

                    else:
                        # If the flow is lesson, the flow-causing actions should be non-deterministic.
                        # E.g., the app code contains Math.random() method.
                        # Retry the current action again.
                        if (prev_taint_history_size > taint_history_size):
                            logger.debug('the flow is lesson, and retry the current action again')

                            actionables.insert(0, action)

                        # If no new flow is detected, do nothing.
                        else:
                            logger.debug('no new leak nor information flow is detected')

                            assert prev_taint_history_size == taint_history_size

                else:
                    # If no app code is executed, skip information flow analysis
                    logger.debug('no app code is executed, and skipping information flow analysis')

                    taint_history_size = 0

            # Exit the outer loop if no new information flow is detected by the inner loop
            if (prev_taint_history_size == taint_history_size):
                return num_leaks_sum

            # Set the taint history size as previous taint history size
            prev_taint_history_size = taint_history_size

    def compare_found_flow(self, leak_taint_histories):
        """
        Compare found flow to previously-found flows.
        """
        for leak_taint_history in leak_taint_histories:
            matched = self.emulator.compare_taint_histories(leak_taint_history)

            if (matched):
                return True

        return False

    def clean(self):
        """
        Kill the app and clear smalien logs on the device.
        """
        logger.debug('clearning')

        self.exerciser.kill()

        # Press back button to clear an alert
        self.exerciser.press_back_button(seconds=2)

        self.exerciser.clear_app_data()

        self.exerciser.clear()

    def perform_flow_causing_actions(self):
        """
        Perform previously-found flow-causing actions.
        """
        logger.debug('performing flow-causing actions')
        logger.debug(self.flow_causing_actions)

        for action in self.flow_causing_actions:
            action()

            self.exerciser.sleep(2)

    def obtain_actionables(self):
        """
        Obtain actionables.
        """
        logger.debug('obtaining actionables')

        actionables = [
            self.launch_and_press_home_button_and_launch,
            # self.launch_and_press_home_button,
            # self.kill_and_launch,
        ]

        # Get tap actions if at least there is a flow-causing action
        if (self.flow_causing_actions):
            logger.debug('obtaining tap actions')

            actionables.extend([
                TapAction(coords, self.exerciser).get() for coords in self.exerciser.get_permutations_of_clickable_ui_coordinates()
            ])
        # Otherwise, app's UI is not visible yet
        else:
            logger.debug('obtaining launch and tap actions')

            # Launch the app
            self.exerciser.launch(seconds=2)

            # Get tap actions
            actionables.extend([
                LaunchTapAction(coords, self.exerciser).get() for coords in self.exerciser.get_permutations_of_clickable_ui_coordinates()
            ])

#         # Append launch action
#         actionables.append(self.exerciser.launch)

        # Get activity actions
        # Activity actions must be performed before service actions in Lifecycle.ServiceEventSequence2
        actionables.extend([
            ActivityAction(activity, self.exerciser).get() for activity in self.app.activities
        ])

        # Get service actions
        actionables.extend([
            ServiceAction(service, self.exerciser).get() for service in self.app.services
        ])

        # Get receiver actions
        actionables.extend([
            ReceiverAction(receiver, self.exerciser).get() for receiver in self.app.receivers
        ])

        # Add other actions
        actionables.extend([
            self.launch_and_press_back_button,
            self.exerciser.kill,
            self.exerciser.rotate_screen,
        ])

        return actionables

    def launch_and_press_home_button_and_launch(self):
        self.exerciser.launch(seconds=2)

        self.exerciser.press_home_button(seconds=2)

        self.exerciser.launch()

#     def launch_and_press_home_button(self):
#         self.exerciser.launch(seconds=2)
# 
#         self.exerciser.press_home_button(seconds=2)
# 
#         self.exerciser.launch()

    def launch_and_press_back_button(self):
        self.exerciser.launch(seconds=2)

        self.exerciser.press_back_button()

#     def kill_and_launch(self):
#         self.exerciser.kill(seconds=2)
# 
#         self.exerciser.launch()
