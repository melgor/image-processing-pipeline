import queue as thq
import multiprocessing as mp
import multiprocessing.queues as mpq


class TaskFlags:
    CONTINUE = "CONTINUE"
    START = "START"
    STOP = "STOP"
    SHUTDOWN = "SHUTDOWN"
    SHUTDOWN_LAST = "SHUTDOWN_LAST"


class IterableQueueThread(thq.Queue):
    def __init__(self, *args, **kwargs):
        super(IterableQueueThread, self).__init__(*args, **kwargs)

    def __iter__(self):
        while True:
            x = self.get()
            if x == TaskFlags.STOP:
                break

            yield x


class IterableQueueProcess(mpq.Queue):
    def __init__(self, *args, **kwargs):
        ctx = mp.get_context()
        super(IterableQueueProcess, self).__init__(*args, **kwargs, ctx=ctx)

    def __iter__(self):
        while True:
            x = self.get()
            if x == TaskFlags.STOP:
                break

            yield x
