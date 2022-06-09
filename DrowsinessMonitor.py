import pandas as pd
from enum import Enum
from datetime import datetime
from PushNotification import sendPushNotification


class States(Enum):
    OPEN = 1
    CLOSED = 2


# The DrowsinessMonitor is monitoring all eye and mouth changes and
# aggregates them to decide if someone is tired, not tired or sleeping
class DrowsinessMonitor:
    _instance = None

    def __init__(self):
        raise RuntimeError('Call instance() instead')

    @classmethod
    def instance(cls):
        if cls._instance is None:
            print('Creating new DataLayer Instance')
            cls._instance = cls.__new__(cls)
            cls.leftEyeDataFrame = pd.DataFrame(columns=['timestamp', 'duration'])
            cls.leftEyeDataFrame["timestamp"] = cls.leftEyeDataFrame["timestamp"].astype("datetime64")
            cls.rightEyeDataFrame = pd.DataFrame(columns=['timestamp', 'duration'])
            cls.rightEyeDataFrame["timestamp"] = cls.rightEyeDataFrame["timestamp"].astype("datetime64")
            cls.mouthDataFrame = pd.DataFrame(columns=['timestamp', 'duration'])
            cls.mouthDataFrame["timestamp"] = cls.mouthDataFrame["timestamp"].astype("datetime64")

            cls.leftEyeState = States.OPEN
            cls.leftEyeClosingTimestamp = datetime.now()
            cls.leftEyeAggregation = pd.DataFrame(columns=['timestamp', 'sum', 'count'])
            cls.rightEyeState = States.OPEN
            cls.rightEyeClosingTimestamp = datetime.now()
            cls.rightEyeAggregation = pd.DataFrame(columns=['timestamp', 'sum', 'count'])
            cls.mouthState = States.CLOSED
            cls.mouthOpeningTimestamp = datetime.now()
            cls.mouthAggregation = pd.DataFrame(columns=['timestamp', 'sum', 'count'])

            cls.tiredNotificationSend = False
            cls.sleepingNotificationSend = False

            cls.fps = 0
        return cls._instance

    def setLeftEyeState(self, state):
        if self.leftEyeState == States.OPEN and state == States.CLOSED:
            self.leftEyeClosingTimestamp = datetime.now()
            self.leftEyeState = States.CLOSED
        elif self.leftEyeState == States.CLOSED and state == States.OPEN:
            duration = datetime.now() - self.leftEyeClosingTimestamp
            self.leftEyeDataFrame = self.leftEyeDataFrame.append({'timestamp': self.leftEyeClosingTimestamp, 'duration': duration.total_seconds()}, ignore_index=True)
            self.leftEyeAggregation = self.getAggregatedDataframe(self.leftEyeDataFrame, 1)
            self.leftEyeState = States.OPEN

    def setRightEyeState(self, state):
        if self.rightEyeState == States.OPEN and state == States.CLOSED:
            self.rightEyeClosingTimestamp = datetime.now()
            self.rightEyeState = States.CLOSED
        elif self.rightEyeState == States.CLOSED and state == States.OPEN:
            duration = datetime.now() - self.rightEyeClosingTimestamp
            self.rightEyeDataFrame = self.rightEyeDataFrame.append({'timestamp': self.rightEyeClosingTimestamp, 'duration': duration.total_seconds()}, ignore_index=True)
            self.rightEyeAggregation = self.getAggregatedDataframe(self.rightEyeDataFrame, 1)
            self.rightEyeState = States.OPEN

    def setMouthState(self, state):
        if self.mouthState == States.CLOSED and state == States.OPEN:
            self.mouthOpeningTimestamp = datetime.now()
            self.mouthState = States.OPEN
        elif self.mouthState == States.OPEN and state == States.CLOSED:
            duration = datetime.now() - self.mouthOpeningTimestamp
            if duration.total_seconds() > 2: # only if duration longer than 2 seconds. To differentiate between talking
                self.mouthDataFrame = self.mouthDataFrame.append({'timestamp': self.mouthOpeningTimestamp, 'duration': duration.total_seconds()}, ignore_index=True)
                self.mouthAggregation = self.getAggregatedDataframe(self.mouthDataFrame, 5)
            self.mouthState = States.CLOSED

    # checks if in the last two minutes the blink rate is above 25 or the yawn rate is above 7 per minute
    # threshold can be adapted
    def isTired(self):
        tired = False
        if (len(self.leftEyeAggregation) > 1 and (
                self.leftEyeAggregation['count'].iloc[-2] > 25 or self.leftEyeAggregation['sum'].iloc[
            -2] > 10)) or \
                len(self.leftEyeAggregation) > 0 and self.leftEyeAggregation['count'].iloc[-1] > 25:
            tired = True
        if (len(self.rightEyeAggregation) > 1 and (
                self.rightEyeAggregation['count'].iloc[-2] > 25 or self.rightEyeAggregation['sum'].iloc[
            -2] > 10)) or \
                len(self.rightEyeAggregation) > 0 and self.rightEyeAggregation['count'].iloc[-1] > 25:
            tired = True
        if (len(self.mouthAggregation) > 1 and self.mouthAggregation['sum'].iloc[-2] > 7) or \
                len(self.mouthAggregation) > 0 and self.mouthAggregation['sum'].iloc[-1] > 7:
            tired = True

        if tired and self.tiredNotificationSend is False:
            sendPushNotification('Müdigkeitserkennung', 'Du scheinst müde zu sein. Bitte nimm eine Auszeit!')
            self.tiredNotificationSend = True

        if not tired:
            self.tiredNotificationSend = False

        return tired

    # checks if both eyes have been closed for at least 10 seconds
    def isSleeping(self):
        sleeping = False
        if self.leftEyeState == States.CLOSED and self.rightEyeState == States.CLOSED:
            leftDuration = datetime.now() - self.leftEyeClosingTimestamp
            rightDuration = datetime.now() - self.rightEyeClosingTimestamp
            if leftDuration.total_seconds() > 10 and rightDuration.total_seconds() > 10:
                sleeping = True

        if sleeping and self.sleepingNotificationSend is False:
            sendPushNotification('Müdigkeitserkennung', 'Du scheinst zu schlafen. Schlaf gut!')
            self.sleepingNotificationSend = True

        if not sleeping:
            self.sleepingNotificationSend = False

        return sleeping

    def setFPS(self, fps):
        self.fps = fps

    # aggregate features for each minute
    def getAggregatedDataframe(self, dataframe, timespan):
        dataframe = dataframe.groupby(pd.Grouper(key='timestamp', freq=f'{timespan}min')).agg(sum=('duration', 'sum'), count=('duration', 'count'))
        return dataframe.reset_index(level=0)

