import multiprocessing as mp
import numpy as np


class ProcessCalculation:
    def __init__(self, tasks: int):
        self.number_cores = mp.cpu_count()  # A number of cores current PC has
        self.tasks = tasks  # A number of processes that should be calculated
        self.separator = int(np.ceil(self.tasks / self.number_cores))  # A number that separates each individual process

        # A number of hypothetical tasks that could be created
        self.number_hypothetical = self.separator * self.number_cores

        self.args = self.get_args()  # Array of processes

    def get_args(self):
        if self.tasks <= 0:
            raise Exception(f"A number of processes is {self.tasks} should be > 0")

        start = 0  # start number of task
        end = self.separator  # end number of task
        args = [{start, end}]  # self.args array

        for i in range(self.number_cores):
            # If end == final task then append last element and return self.args
            if end == self.tasks:
                args.append({start, end})
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

            # swap (end,start) and add separator * 2 to end
            end, start = start, end
            end += self.separator * 2

            args.append({start, end})

    def show_args(self):
        print(self.args)
