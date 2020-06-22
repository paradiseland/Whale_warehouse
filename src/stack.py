class Stack:
    """
    define a stack class to imitate operations in the stack of a warehouse.
    """
    def __init__(self, h, h_available):
        self.items = []
        self.height = h
        self.height_available = h_available

    def is_empty(self):
        return self.items == []

    def is_peek(self, tier):
        return tier == self.size()-1

    def size(self):
        return len(self.items)

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

