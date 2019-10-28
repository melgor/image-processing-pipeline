# source : https://gist.github.com/smhanov/8fb48199338045fc5e69fd615211c84c

from multiprocessing import Process, Queue
import inspect

STOP = "STOP"
SHUTDOWN = "SHUTDOWN"
SHUTDOWN_LAST = "SHUTDOWN_LAST"


class Task(object):
    def __init__(self, process_id, object_runable, input_queue, output_queue, processes):
        self.process_id = process_id
        self.processes = processes
        self.object_runable = object_runable
        self.process = None
        self.source = None
        self.input_queue = input_queue
        self.output_queue = output_queue

    def start(self):
        self.process = Process(target=self.main, args=(self.object_runable,  self.input_queue, self.output_queue))
        self.process.start()

    def main(self, object_runable, input_queue, output_queue):
        try:
            while True:
                input = input_queue.get()

                # In case of shutdown, also inform other to shutdown
                if input == SHUTDOWN:
                    break
                if input == SHUTDOWN_LAST:
                    output_queue.put(STOP)
                    break
                if input == STOP:
                    for i in range(self.processes - 1):
                        input_queue.put(SHUTDOWN)
                    input_queue.put(SHUTDOWN_LAST)
                    continue

                # run results
                result = object_runable(input)

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

            object_runable.shutdown()

        except KeyboardInterrupt:
            pass
        except Exception:
            print("For {}".format(self))


class PipelineManager:
    def __init__(self):
        self.tasks = []
        self.nextId = 1
        self.input_queue = Queue(32)
        self.output_queue = Queue(32)

    def run(self, arg=None):

        for task in self.tasks:
            task.start()

        self.input_queue.put(arg)
        while True:
            x = self.output_queue.get()
            if x == STOP:
                break

    def add(self, object_runable, process=1):
        input_queue = self.input_queue
        if len(self.tasks):
            # set output queue for last_task which have same output as input for next one
            input_queue = Queue(32)
            for task in self.tasks:
                if task.output_queue == self.output_queue:
                    task.output_queue = input_queue

        # create task for every process. Task share queue
        for i in range(process):
            task = Task(self.nextId, object_runable, input_queue, self.output_queue, process)
            self.nextId += 1
            self.tasks.append(task)




