import logging
import pathlib
import glob

from .class_parser import ClassParser
from .field_parser import FieldParser
from .method_parser import MethodParser
from .instruction_parser import InstructionParser

logger = logging.getLogger(name=__name__)


class ParserManager():
    """
    Manage parsers of classes, fields, methods, and bytecode instructions in smali files.
    """

    def __init__(self, app, ignore_list, target_packages, taint_sources, taint_sinks):
        logger.debug('initializing')
        self.app = app
        self.root = str(app.unpackaged)
        self.ignore_list = ignore_list
        self.target_packages = target_packages
        self.taint_sources = taint_sources
        self.taint_sinks = taint_sinks

        self.cparser = ClassParser(self.root, self.app.classes, app.dex_ids)

        self.referenced_methods = []

    def run(self):
        """
        Execute the parsing.
        """
        logger.debug('running')

        # Search for smali files in the unpackaged directory
        smali_paths = glob.iglob(self.root+'/**/*.smali', recursive=True)

        # Parse classes in smali files.
        cid = 0
        for path in smali_paths:
            if (path.find(self.root+'/smali_assets') < 0 and
                path.find(self.root+'/assets') < 0
               ):
                self.parse_class(cid, path)
                cid += 1

        # Exit if no class is parsed
        if (len(self.app.classes.keys()) == 0):
            raise Exception('No class is parsed')

        # Find classes' families
        [self.cparser.find_families(clss) for clss in self.app.classes.values()]

        # Parse fields in classes
        [self.parse_fields(clss) for clss in self.app.classes.values()]

        # Parse methods in classes
        [self.parse_methods(clss) for clss in self.app.classes.values()]

        # Parse instructions in methods
        [self.parse_instructions(clss) for clss in self.app.classes.values()]

    def check_ignore_list(self, path_in_dex):
        """
        Check if the given class is in the ignore list.
        Return True if so.
        """
        for ignored_class in self.ignore_list:
            if (path_in_dex.startswith(ignored_class.lstrip('/'))):
                return True

        return False

#     def check_target_packages(self, smali_path):
#         """
#         Check if the given class is one of the target packages.
#         Return True if so.
#         Always return True if target package is empty.
#         """
#         if (len(self.target_packages) < 1):
#             return True
# 
#         class_path = smali_path.replace(self.root, '')
# 
#         for target_package in self.target_packages:
#             # Convert package name to directory structure
#             target_package = target_package.replace('.', '/')
# 
#             if (class_path.find(target_package) > -1):
#                 return True
# 
#         return False

    def parse_class(self, cid, smali_path):
        """
        Parse a class in the given smali file.
        """
        # Check if the class is in the ignore list
        # ignore = self.check_ignore_list(smali_path)
        # if (ignore):
        #     return

        # Currently disabled
#         # Continue only if the class is one of target packages
#         is_target = self.check_target_packages(smali_path)
#         if (not is_target):
#             return

        # Parse the class
        app_class = self.cparser.run(cid, smali_path)

        # Check if the class is in the ignore list
        app_class.ignore = self.check_ignore_list(app_class.path_in_dex)

        self.app.classes[app_class.name] = app_class
        self.app.cids[app_class.cid] = app_class

    def parse_fields(self, clss):
        """
        Parse fields in the given class.
        """
        logger.debug('parsing field')
        try:
            FieldParser(clss.linage, clss.code, clss.fields).run()
        except Exception as e:
            raise Exception(f'Field parser failed, {clss.path = }') from e

    def parse_methods(self, clss):
        """
        Parse methods in the given class.
        """
        logger.debug('parsing method')
        try:
            MethodParser(clss, clss.name, clss.linage, clss.code, clss.methods).run()
        except Exception as e:
            raise Exception(f'Method parser failed, {clss.path = }') from e

    def parse_instructions(self, clss):
        """
        Parse instructions in the given method's body.
        """
        try:
            for m in clss.methods.values():
                # The InstructionParser instance keeps data of a method
                # Hence, a different instance should be used for a different method
                clss.reference_num += InstructionParser(m,
                                                        clss.code,
                                                        clss.parent,
                                                        self.app.classes,
                                                        self.referenced_methods,
                                                        self.taint_sources,
                                                        self.taint_sinks).run()
                # Count potential sources and sinks
                if (not clss.ignore):
                    self.app.num_potential_sources += m.num_potential_sources
                    self.app.num_potential_sinks += m.num_potential_sinks

            # Count total reference num
            self.app.reference_num += clss.reference_num

        except Exception as e:
            raise Exception(f'Instruction parser failed, {clss.path = }') from e
