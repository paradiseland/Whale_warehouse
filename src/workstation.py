import random
from CONSTANT import WIDTH, T_p


class Workstation:
    """
    define a workstation class to describe available workstation and its state.
    """

    def __init__(self, code: int):

        self.num_of_workstations = WIDTH
        self.place_x = code
        self.place_y = -1

    def pick_up(self, max_process_time=T_p[0], min_process_time=T_p[1]):
        return random.uniform(min_process_time, max_process_time)


