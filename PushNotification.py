import os


def notifyOnMac(title, message):
    os.system("""
              osascript -e 'display notification "{}" with title "{}"'
              """.format(message, title))


def notifyOnWindows(title, message):
    from win10toast import ToastNotifier
    toast = ToastNotifier()
    toast.show_toast(
        title,
        message,
        duration=20,
        threaded=True,
    )


def sendPushNotification(title, message):
    if os.name == 'nt':
        notifyOnWindows(title, message)
    else:
        notifyOnMac(title, message)