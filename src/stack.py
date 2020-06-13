class Stack:
    """
    define a stack class to imitate operations in the stack of a warehouse.
    """
    def __init__(self, H, TAU):
        self.items = []
        self.available = int(H*(1-TAU))

    def is_empty(self):
        return self.items == []

    def peek(self):
        return self.items[len(self.items) - 1]

    def size(self):
        return len(self.items)

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    def pop_ordered(self, designated_place):
        """
        ------------
        Return
        designated place and blocking bins as list.
        """
        poped = (self.items[designated_place], self.items[designated_place+1:])

        self.items = self.items[:designated_place]
        return poped
