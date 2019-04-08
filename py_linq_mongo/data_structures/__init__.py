from collections import deque


class Stack(object):
    """
    Encapsulates logic of a stack
    """
    def __init__(self):
        self.items = deque()

    def pop(self):
        if len(self.items) == 0:
            return None
        return self.items.popleft()

    def push(self, item):
        self.items.appendleft(item)
