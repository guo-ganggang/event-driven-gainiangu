import datetime


class Timer(object):

    def __init__(self):
        self.start = datetime.datetime.now()
        self.end = self.start
        self.duration = self.end - self.start

    def click(self):
        self.end = datetime.datetime.now()
        self.duration = self.end - self.start
        return self.duration

    def reset(self):
        self.start = datetime.datetime.now()
        self.end = self.start
        self.duration = self.end - self.start
