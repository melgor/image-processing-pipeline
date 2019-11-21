# source : https://gist.github.com/smhanov/8fb48199338045fc5e69fd615211c84c

from multiprocessing import Process, Queue, Lock, Manager
from multiprocessing.queues import Full, Empty
import time

import inspect

CONTINUE = "CONTINUE"
STOP = "STOP"
SHUTDOWN = "SHUTDOWN"
SHUTDOWN_LAST = "SHUTDOWN_LAST"


class GeneralQueue:
    def __init__(self, maxsize, name="Input_Queue"):
        self.queue = Queue(maxsize=maxsize)
        self.name = name
        self.done = False

    def __iter__(self):
        while True:
            x = self.get()

            if x == CONTINUE:
                continue

            if x == STOP:
                print("STOP ", self.name, self.done, self.queue.empty())
                self.done = True
                continue

            if x == SHUTDOWN:
                break

            yield x
        print("BREAK ", self.name, self.done, self.queue.empty())

    def get(self):
        try:
            x = self.queue.get(timeout=1)
        except (Full, Empty):
            time.sleep(.05)
            print("Wait ", self.name, self.done, self.queue.empty())
            return SHUTDOWN if self.done else CONTINUE
        else:
            return x

    def put(self, x):
        self.queue.put(x)


m = multiprocessing.Manager()
    q = m.Queue()

class Task:
    def __init__(self, callable_object, processes=1, max_size=32):
        self.processes = processes
        self.other_processes = 1
        self.callable_object = callable_object
        self.input_queue = GeneralQueue(maxsize=max_size)
        self.output_queue = GeneralQueue(maxsize=max_size, name=callable_object.__class__.__name__ + "_Queue")
        self.start_previous_process = None

    def __iter__(self):
        self.start()
        for x in self.output_queue:
            if x == STOP:
                raise StopIteration
            yield x

    def start(self):

        for idx in range(self.processes):
            process = Process(target=self.run, args=(self.callable_object, self.input_queue, self.output_queue,
                                                     self.other_processes, idx))
            process.start()

        if self.start_previous_process is not None:
            self.start_previous_process()
        else:
            # mean that this is first Task, put None in input_queue to start all pipeline and then STOP it
            self.input_queue.put(None)
            self.input_queue.put(STOP)

    def __or__(self, other):
        other.input_queue = self.output_queue
        other.start_previous_process = self.start
        self.other_processes = other.processes
        return other

    @staticmethod
    def run(callable_object, input_queue, output_queue, other_processes, idx):
        for input_data in input_queue:
            result = callable_object(input_data)
            # in case of generator, input all elements from into output_queue
            if inspect.isgenerator(result):
                [output_queue.put(x) for x in result]
            else:
                output_queue.put(result)

        callable_object.shutdown()
        for _ in range(other_processes):
            output_queue.put(STOP)
        print("STOP PROCESS:", callable_object.__class__.__name__ , idx)




