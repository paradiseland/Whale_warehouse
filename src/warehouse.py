from stack import Stack
from CONSTANT import TAU, HEIGHT_AVAILABLE, WIDTH, LENGTH, HEIGHT
import numpy as np


class Warehouse:
    """
    Define a Warehouse class to get an available place and to save parameters of warehouse configuration.
    """

    def __init__(self,cell):
        self.cell = cell
        self.WIDTH = WIDTH
        self.LENGTH = LENGTH
        self.HEIGHT = HEIGHT
        self.HEIGHT_AVAILABLE = HEIGHT_AVAILABLE

        self.ratio = self.WIDTH / self.LENGTH
        self.record = [[Stack(self.HEIGHT, self.HEIGHT_AVAILABLE) for i in range(self.LENGTH)]
                       for j in range(self.WIDTH)]
        self.init_record()

    def init_record(self):
        # initialize a warehouse storage.
        tmp = np.ones(self.avail_capacity, dtype=np.bool)
        index_cell = np.arange(self.avail_capacity)
        random_choose = np.random.choice(index_cell, int(self.avail_capacity/2), replace=False).tolist()
        for i in random_choose:
            tmp[i] = False
        stack_height = np.sum(tmp.reshape((-1, self.HEIGHT_AVAILABLE)), axis=1).reshape(self.WIDTH, self.LENGTH)
        for width in range(self.WIDTH):
            for length in range(self.LENGTH):
                self.record[width][length].items = [1] * stack_height[width, length]

    @property
    def capacity(self):
        return self.WIDTH * self.LENGTH * self.HEIGHT

    @property
    def avail_capacity(self):
        return self.WIDTH * self.LENGTH * self.HEIGHT_AVAILABLE

    @property
    def current_storage(self):
        return np.sum(self.get_stacks_state)

    @property
    def get_stacks_state(self):
        return np.array([self.record[i][j].size() for i in range(self.WIDTH) for j in range(self.LENGTH)])

    # @staticmethod
    # def get_line_state(psbs) -> list:
    #     """
    #     whether each line has a available psb.
    #     """
    #     state = [0] * psbs.num_psbs
    #     for line in [psb.current_line for psb in psbs]:
    #         state[line] = 1
    #     return state

    def rand_place(self) -> tuple:
        """
        ---------------
        Return x_y place, stack tier
        """
        tmp = np.random.choice(self.current_storage)
        cum_sum = self.get_stacks_state.cumsum().reshape(self.WIDTH, self.LENGTH)
        pre_place = tuple(np.argwhere(cum_sum <= tmp)[-1].tolist())
        place = tuple(np.argwhere(cum_sum > tmp)[0].tolist())
        stack_tier = tmp - cum_sum[pre_place]

        return place, stack_tier

