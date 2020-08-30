from datetime import datetime


class Timer(object):
    def __init__(self):
        self.start_time = datetime.now()
        self.end_time = self.start_time
        self.duration = self.end_time - self.start_time

    def click(self):
        """

        :return: How many seconds have passed
        """
        self.end_time = datetime.now()
        self.duration = self.end_time - self.start_time
        seconds = self.duration.seconds

        return seconds

    def reset(self):
        """
        Reset all the member variables
        :return:
        """
        self.start_time = datetime.now()
        self.end_time = self.start_time
        self.duration = self.end_time - self.start_time
