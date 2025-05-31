import time


class CT:
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.elapsed_time = None

    def start(self):
        self.start_time = time.time()

    def stop(self):
        if self.start_time is None:
            raise RuntimeError("Should use start() before stop()")
        self.end_time = time.time()
        self.elapsed_time = self.end_time - self.start_time
        return self.elapsed_time
