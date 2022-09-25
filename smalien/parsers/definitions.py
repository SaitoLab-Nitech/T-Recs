
"""
Mapping app methods' attributes.
"""
METHOD_ATTRIBUTES = [
    [' native ',   'native'],
    [' abstract ', 'abstract'],
    [' static ',   'static'],
    ['',           'normal']
]

"""
Mapping methods to whether having bytecode implementation.
"""
IMPLEMENTEDS = {
    'native': False,
    'abstract': False,
    'static': True,
    'normal': True,
}

"""
Regular expression string for detecting data types of a method's arguments.
"""
RE_METHOD_ARG_TYPES = r'\[*[VZBSCIJFD](?![a-z])|\[*L.+?;'


"""
Special API methods.
Currently, smalien detects the methods without this predefined list.
"""
# SPECIAL_API_METHODS = {
#     'reflection': {
#         'Ljava/lang/reflect/Method;': [
#             'invoke(Ljava/lang/Object;[Ljava/lang/Object;)Ljava/lang/Object;',
#         ],
#     },
#     'threading': {
#         # Invoking method doInBackground([Ljava/lang/Object;)Ljava/lang/Object;
#         'Landroid/os/AsyncTask;': [
#             'execute([Ljava/lang/Object;)Landroid/os/AsyncTask;',
#         ],
#     },
# }
