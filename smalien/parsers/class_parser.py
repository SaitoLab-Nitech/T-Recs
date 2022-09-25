import logging

from ..structures import AppClass

logger = logging.getLogger(name=__name__)


class ClassParser:
    """
    Parse app classes in smali files.
    """

    def __init__(self, root, classes, dex_ids):
        logger.debug('initializing')

        self.root = root
        self.classes = classes
        self.dex_ids = dex_ids

    def run(self, cid: int, path: str):
        """
        Execute the class parser.
        Return None if the given class is in the ignore_list.
        """
        logger.debug('running')

        # Load smali code
        with open(path, 'r') as f:
            code = f.read().split('\n')

            # Create an app class object
            app_class = AppClass(cid=cid,
                                 name=self.get_class_name(code[0]),
                                 path=path,
                                 is_abstract=self.check_whether_class_is_abstract(code[0]),
                                 parent=self.get_parent_class(code[1], path),
                                 linage=len(code),
                                 code=code,
                                 dex_id=self.get_dex_id(path),
                                 path_in_dex=self.get_path_in_dex(path))

        return app_class

    def get_class_name(self, line):
        """
        Extract the class name.
        """
        return line.split(' ')[-1]

    def check_whether_class_is_abstract(self, line):
        """
        Check whether the given class is abstract.
        """
        if (line.find(' abstract ') > -1):
            return True
        return False

    def get_parent_class(self, line, path):
        """
        Extract the class's parent class.
        """
        if (line.startswith('.super')):
            return line.split(' ')[-1]

        logger.debug(f'The parent does not found at {line} in {path}')
        return None

    def get_dex_id(self, path):
        """
        Extract dex id in the path.
        """
        dex_id = path[len(self.root):].split('/')[1]

        self.dex_ids.add(dex_id)

        return dex_id

    def get_path_in_dex(self, path):
        """
        Extract smali file's path in dex.
        """
        return '/'.join(path[len(self.root):].split('/')[2:])

    def find_families(self, app_class):
        """
        Generate a conservative set of inherited classes of each app class.
        """
        logger.debug('finding class families')
        ancestors = set()
        self.find_ancestors(app_class.name, app_class.parent, ancestors)

        app_class.family |= ancestors

    def find_ancestors(self, me, parent, ancestors):
        """
        Find the class's ancestors.
        Update descendants at the same time.
        """
        if (parent is not None and parent not in ancestors):
            ancestors.add(parent)
            if (parent in self.classes.keys()):
                self.classes[parent].family |= {me} | self.classes[me].family
                self.find_ancestors(parent, self.classes[parent].parent,
                                    ancestors)
