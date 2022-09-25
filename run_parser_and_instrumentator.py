import smalien
import sys
import logging


def run_parser_and_instrumentator():
    # Setup the log level
    logging.getLogger('smalien').setLevel('DEBUG')

    # Setup ignore package list
    # ignore_list = []
    ignore_list = [ 'android', 'androidx' ]

    project = smalien.Project(sys.argv[1], ignore_list=ignore_list)

    project.configure_keystore(keystore='<path_to_your_key>',
                               storepass='<keystore_password>',
                               keypass='<key_password>',
                               alias='<key_alias_name>')

    # Run instrumentator
    project.instrument()
    # For real-world apps, it's better to use these options for instrumentator
    # project.instrument(log_buff_size=5000,
    #                    register_reassignment=True)

    project.create_new_apk()

    project.save()

if __name__ == '__main__':
    run_parser_and_instrumentator()
