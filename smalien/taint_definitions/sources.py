
# TODO: For user input validation detection, track const and sharedpreferences
# so that smalien can detect it without InputScope.
taint_sources = {
    'Landroid/telephony/TelephonyManager;': {
        'getDeviceId()Ljava/lang/String;': 'IMEI',
        # 'getDeviceId(I)Ljava/lang/String;': 'IMEI',  # Not necessary for DroidBench
        # 'getImei()Ljava/lang/String;': 'IMEI',       # Not necessary for DroidBench
        'getSimSerialNumber()Ljava/lang/String;': 'ICCID',
        'getSubscriberId()Ljava/lang/String;': 'IMSI',
    },
    'Landroid/location/Location;': {
        'getLatitude()D': 'Latitude',
        'getLongitude()D': 'Longitude',
    },
}
