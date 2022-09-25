import logging
import pathlib

from .utils.pickle_handler import PickleHandler
from .parsers.parser_manager import ParserManager
from .structures import App, AppClass, AppField, AppMethod

logger = logging.getLogger(name=__name__)

def load_pickle(**kwargs):
    """
    Load a target's pickle.

    :param target:    Path to pickle file.
    """
    logger.debug('loading pickle')

    return PickleHandler.load(kwargs['target'])

def load_apk(**kwargs):
    """
    Load a target's apk.

    :param target:       Path to target apk.
    :param workspace:    Path to workspace directory.
    :param ignore_list:  List of packages to be skipped.
    :param apk_handler:  ApkHandler object.
    :param run_parser:   Whether run parser.
    """
    logger.debug('loading apk')

    apk = kwargs['target']
    workspace = kwargs['workspace']
    ignore_list = kwargs['ignore_list']
    target_packages = kwargs['target_packages']
    apk_handler = kwargs['apk_handler']
    taint_sources = kwargs['taint_sources']
    taint_sinks = kwargs['taint_sinks']

    # Get app's package name
    package = apk_handler.get_package_name(apk)
    # Get app's component names
    services, receivers, activities = apk_handler.get_components(apk, package)

    # For smalien log path
    smalien_log = kwargs['smalien_log']
    smalien_log_local = workspace / pathlib.Path(smalien_log).name

    # Initialize an app data object
    app = App(apk=apk,
              name=apk.name,

              # App's information for exercising
              package=package,
              services=services,
              receivers=receivers,
              activities=activities,

              # Paths
              pickled=workspace / (apk.stem+'.pickle'),
              smaliened=workspace /  ('smaliened_'+apk.name),
              unpackaged=workspace / apk.stem,
              smalien_log=smalien_log,
              smalien_log_local=smalien_log_local,
              android_manifest=workspace / apk.stem / 'AndroidManifest.xml',
              logcat_log=workspace / 'logcat.log')

    # Run parse if run_parser is True
    if (kwargs['run_parser']):
        # Unpackage the apk
        app.resource_decoded = apk_handler.unpackage(apk, app.unpackaged, app.smaliened)

        # Parse app code
        ParserManager(app, ignore_list, target_packages, taint_sources, taint_sinks).run()

        # Analyze
        # TODO: Implement analyzers

    return app

class Loader:
    """
    Load a target's data from pickle or apk.
    """
    loaders = {
        '.pickle': load_pickle,
        '.apk': load_apk,
    }
