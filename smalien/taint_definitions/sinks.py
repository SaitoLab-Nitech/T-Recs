
# Annotating the offset of argument containing sensitive information in DroidBench.
# The offset is calculated without considering base object as an argument.

taint_sinks = {
    'Landroid/telephony/SmsManager;': {
        'sendTextMessage(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Landroid/app/PendingIntent;Landroid/app/PendingIntent;)V': 'sink',  # Third argument
    },
    'Landroid/util/Log;': {
        'i(Ljava/lang/String;Ljava/lang/String;)I': 'sink',  # Second argument
        'e(Ljava/lang/String;Ljava/lang/String;)I': 'sink',  # Second argument
        'v(Ljava/lang/String;Ljava/lang/String;)I': 'sink',  # Second argument
        'd(Ljava/lang/String;Ljava/lang/String;)I': 'sink',  # Second argument
    },
    'Ljava/lang/ProcessBuilder;': {
        'start()Ljava/lang/Process;': 'sink',  # Base object
    },
    'Landroid/app/Activity;': {
        'startActivityForResult(Landroid/content/Intent;I)V': 'sink',  # First argument
        'setResult(ILandroid/content/Intent;)V': 'sink',  # Second argument
        'startActivity(Landroid/content/Intent;)V': 'sink',  # First argument
        # This is not included in Zhang2021, but necessary to detect a sink in BroadcastTaintAndLeak1
        'sendBroadcast(Landroid/content/Intent;)V': 'sink',  # First argument
    },
    'Ljava/net/URL;': {
        'openConnection()Ljava/net/URLConnection;': 'sink',  # Base object
    },
    'Landroid/content/ContextWrapper;': {
        'sendBroadcast(Landroid/content/Intent;)Z': 'sink',  # First argument
    },

    # Below sinks are not included in Zhang2021, but necessary to detect sinks in some apps.
    'Landroid/content/Context;': {
        'startActivity(Landroid/content/Intent;)V': 'sink',  # First argument
    },
    'Landroid/telephony/gsm/SmsManager;': {
        'sendTextMessage(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Landroid/app/PendingIntent;Landroid/app/PendingIntent;)V': 'sink',  # Third argument
    },
}
