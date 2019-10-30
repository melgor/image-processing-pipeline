# source : https://gist.github.com/smhanov/8fb48199338045fc5e69fd615211c84c

from multiprocessing import Process, Queue
import inspect

STOP = "STOP"
SHUTDOWN = "SHUTDOWN"
SHUTDOWN_LAST = "SHUTDOWN_LAST"


class Task(object):
    def __init__(self, callable_object, processes=1, max_size=32):
        self.processes = processes
        self.callable_object = callable_object
        self.process = None
        self.source = None
        self.input_queue = Queue(maxsize=max_size)
        self.output_queue = Queue(maxsize=max_size)
        self.start_other = None

    def __iter__(self):
        self.start()
        while True:
            x = self.output_queue.get()
            if x == STOP:
                raise StopIteration
            yield x

    def start(self):
        for idx in range(self.processes):
            self.process = Process(target=self.main, args=(self.callable_object,  self.input_queue, self.output_queue))
            self.process.start()

        if self.start_other is not None:
            self.start_other()
        else:
            # mean that this is first Task, put sth in input_queue
            self.input_queue.put(None)

    def __or__(self, other):
        other.input_queue = self.output_queue
        other.start_other = self.start
        return other

    def main(self, callable_object, input_queue, output_queue):
        try:
            while True:
                input_data = input_queue.get()

                # In case of shutdown, also inform other to shutdown
                if input_data == SHUTDOWN:
                    break
                if input_data == SHUTDOWN_LAST:
                    output_queue.put(STOP)
                    break
                if input_data == STOP:
                    for i in range(self.processes - 1):
                        input_queue.put(SHUTDOWN)
                    input_queue.put(SHUTDOWN_LAST)
                    continue

                # run results
                result = callable_object(input_data)

                # in case of generator, input all elements from into output_queue
                if inspect.isgenerator(result):
                    for x in result:
                        if x == STOP:
                            input_queue.put(STOP)
                            break
                        output_queue.put(x)
                else:
                    if result == STOP:
                        input_queue.put(STOP)
                    else:
                        output_queue.put(result)

            callable_object.shutdown()

        except KeyboardInterrupt:
            pass
        except Exception:
            print("For {}".format(self))




