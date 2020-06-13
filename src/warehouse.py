import numpy
from stack import Stack
from CONSTANT import TAU


class Warehouse:
    """
    Define a Warehouse class to get an available place and to save parameters of warehouse configuration.
    """

    def __init__(self, width, length, height):
        self.width = width
        self.length = length
        self.height = height
        self.ratio = self.width / self.length
        self.record = [[Stack(self.height, TAU) for i in range(self.length)]
                       for j in range(self.width)]

    @property
    def capacity(self):
        return self.width * self.length * self.height

    def pick_up(self, xy, stack_place):
        """
        reshuffle the stack to get the designated bin.[x, y, stack_place]
        """
        current_stack = self.record[xy[0]][xy[1]]
        if stack_place == current_stack.size():
            current_stack.pop()
        else:
            blocking_bins = self.reshuffle()

    def drop_off(self, place, product=1):
        self.record[place[0]][place[1]].push(product)

    def reshuffle(self, stack_place):

        return blocking

    def return_blocking_bins(self):
        pass
