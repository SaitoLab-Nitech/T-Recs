import logging
import os
import glob
import shutil

from smalien.definitions import REF_LIMIT_IN_DEX

logger = logging.getLogger(name=__name__)


class Relocator:
    """
    Relocate smali files to avoid 64k reference limit problem.
    """

    def __init__(self, app):
        logger.debug('initializing')

        self.app = app

    def run(self):
        logger.debug('running')

        unused_dex_path = None

        # Relocate the app's smali files in each dex
        for dex_id in self.app.dex_ids:

            move_smalis = False
            reference_num_sum = 0

            for class_data in self.app.classes.values():
                if (class_data.dex_id == dex_id):
                    # logger.warning(class_data.path)
                    # logger.warning(class_data.reference_num)
                    # logger.warning(class_data.dex_id)

                    reference_num_sum += class_data.reference_num

                    if (reference_num_sum > REF_LIMIT_IN_DEX):
                        move_smalis = True

                        unused_dex_path = self.update_unused_dex_id(unused_dex_path)

                        # Reset the ref counter
                        reference_num_sum = class_data.reference_num

                    if (move_smalis):
                        # Move the smali file
                        self.move_smali(class_data.path, unused_dex_path/class_data.path_in_dex)

        # Relocate Smalien's smali files
        for i, smalien_smali_path in enumerate(glob.glob(str(self.app.unpackaged / self.app.smalien_dex_id / 'SmalienLog_*'))):
            # logger.warning(f'{smalien_smali_path = }')
            if (i > 0):
                # Update unused dex path, and move the smali file
                unused_dex_path = self.update_unused_dex_id(unused_dex_path)
                self.move_smali(smalien_smali_path, unused_dex_path / smalien_smali_path.split('/')[-1])

    def update_unused_dex_id(self, current_dex_path):
        """
        Update the unused dex id.
        """
        if (current_dex_path is None):
            dex_id = self.app.smalien_dex_id
        else:
            dex_id = current_dex_path.name

        num = int(dex_id.replace('smali_classes', ''))

        return self.app.unpackaged / f'smali_classes{num+1}'

    def move_smali(self, src, dst):
        """
        Move the given smali file from <src> to <dst>.
        """
        logger.debug('moving smali')

        logger.debug(f'{src = }')
        logger.debug(f'{dst = }')

        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.move(src, dst)

        self.remove_empty_dirs(src)

    def remove_empty_dirs(self, path):
        """
        Remove empty dirs on the given path.
        """
        while True:
            dir_name = os.path.dirname(path)
            if (os.listdir(dir_name) == []):
                os.rmdir(dir_name)
                path = dir_name
            else:
                break
