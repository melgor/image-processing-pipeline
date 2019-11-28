from .queue import IterableQueueThread, IterableQueueProcess, TaskFlags
import threading as th
import multiprocessing as mp
import inspect
from abc import ABC


class AbstractWorker(ABC):
    def __init__(self, callable_object, input_queue, output_queue, other_processes, **kwargs):
        self.callable_object = callable_object
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.other_processes = other_processes
        super().__init__(**kwargs)

    def run(self):
        for input_data in self.input_queue:

            result = self.callable_object(input_data)
            # in case of generator, input all elements from into output_queue
            if inspect.isgenerator(result):
                [self.output_queue.put(x) for x in result]
            else:
                self.output_queue.put(result)

        self.callable_object.shutdown()
        for _ in range(self.other_processes):
            self.output_queue.put(TaskFlags.STOP)


class SingleTask:
    def __init__(self, **kwargs):
        pass

    def start(self):
        self.run()


class Task(ABC):

    class Worker(AbstractWorker, SingleTask):
        pass

    def __init__(self, callable_object, processes=1, max_size=32):
        self.processes = processes
        self.other_processes = 1
        self.callable_object = callable_object
        self.input_queue = IterableQueueThread(maxsize=max_size)
        self.output_queue = IterableQueueThread(maxsize=max_size)
        self.start_previous_process = None
        self.process = []
        self.idx_process = 0

    def __iter__(self):
        self.start()
        for x in self.output_queue:
            if x == TaskFlags.STOP:
                raise StopIteration
            yield x

    def start(self):
        for idx in range(self.processes):
            process = self.Worker(self.callable_object, self.input_queue, self.output_queue,
                                  self.other_processes, daemon=True)
            if self.idx_process == 0:
                # mean that this is first Task, put None in input_queue to start all pipeline and then STOP it
                self.input_queue.put(TaskFlags.START)
                self.input_queue.put(TaskFlags.STOP)
            process.start()
            self.process.append(process)

        if self.start_previous_process is not None:
            self.start_previous_process()

    def __or__(self, other):
        # Take input Queue from other process and set it as output of current process
        # to enable sending data between them
        # In case of Thread-Process communication, all Queue need to be Process type
        if any([isinstance(self, ProcessTask), isinstance(other, ProcessTask)]):
            # change type of Queue to Process
            self.output_queue = IterableQueueProcess(maxsize=32)

        other.input_queue = self.output_queue
        other.start_previous_process = self.start
        self.other_processes = other.processes
        other.idx_process = self.idx_process + 1
        return other


class ProcessTask(Task):

    class Worker(AbstractWorker, mp.Process):
        pass

    def __init__(self, callable_object, processes=1, max_size=32):
        super().__init__(callable_object, processes=processes, max_size=max_size)
        self.input_queue = IterableQueueProcess(maxsize=max_size)
        self.output_queue = IterableQueueProcess(maxsize=max_size)


class ThreadTask(Task):
    """
    ThreadTask run Thread for callable object. Also it create Thread Queue for sending data between Threads
    """
    class Worker(AbstractWorker, th.Thread):
        pass
