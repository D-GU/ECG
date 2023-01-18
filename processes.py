import multiprocessing as mp
import numpy as np


class ProcessCalculation:
    def __init__(self, tasks: int, target):
        self.target = target  # A target to calculate
        self.number_cores = mp.cpu_count()  # A number of cores current PC has
        self.tasks = tasks  # A number of processes that should be calculated
        self.task_box = []  # An array containing all the processes

        # A number that separates each individual process boundaries
        self.separator = int(
            np.ceil(self.tasks / self.number_cores)
        )

        # A number of hypothetical tasks that could be created
        self.number_hypothetical = self.separator * self.number_cores

        self.boundaries = self.get_boundaries()  # Array of processes

    def get_boundaries(self):
        if self.tasks <= 0:
            raise Exception(f"A number of processes is {self.tasks} should be > 0")

        start = 0  # start number of task
        end = self.separator  # end number of task
        args = [[start, end]]  # self.args array

        for i in range(self.number_cores):
            # If end == final task then append last element and return self.args
            if end == self.tasks:
                args.append([start, end])
                return args

            # If number is about to go above boundaries
            if end + self.separator > self.tasks:
                # swapping (start, end)
                temp = end
                start = temp

                # Difference number between hypothetical task number and real task number
                difference = (start + self.separator) - self.tasks

                # end = final real task number
                end = start + self.separator - difference
                continue

            # swap (end, start) and add separator * 2 to end
            end, start = start, end
            end += self.separator * 2

            args.append([start, end])

    def get_task_box(self, q):
        for i in range(self.number_cores):
            # Append a task box with process to calculate (each process comes with its own boundaries)
            self.task_box.append(
                mp.Process(
                    target=self.target, args=(self.boundaries[i][0], self.boundaries[i][1], 12, q), name=f"task_{i}")
            )

        return np.array(self.task_box)

    def show_args(self):
        print(self.boundaries)

