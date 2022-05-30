import os

def notifyOnMac(title, text):
    os.system("""
              osascript -e 'display notification "{}" with title "{}"'
              """.format(text, title))

notifyOnMac("Drowsiness Detection", "Seems like you are tired")