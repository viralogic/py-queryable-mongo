from collections import deque
import copy


class Stack(object):
    """
    Encapsulates logic of a stack
    """
    def __init__(self, items=None):
        if items is not None:
            if not isinstance(items, deque):
                raise AttributeError("items is not a deque instance")
        self.items = deque() if items is None else items

    def __len__(self):
        return len(self.items)

    def top(self):
        """
        Peeks at the item at top of stack without removing it
        """
        if len(self.items) == 0:
            return None
        item = self.pop()
        self.push(item)
        return item

    def pop(self):
        """
        Removes top of the stack
        """
        if len(self.items) == 0:
            return None
        return self.items.popleft()

    def push(self, item):
        """
        Pushes item onto top of stack
        """
        self.items.appendleft(item)

    def clear(self):
        """
        Removes all items from the stack
        """
        self.items.clear()

    def copy(self):
        """
        Deep copies stack into a new stack
        """
        stack = Queue()
        for i in self.items:
            if i is None:
                continue
            cpy = copy.deepcopy(i)
            stack.push(cpy)
        return Stack(items=stack.items)

    def reverse(self):
        """
        Reverses the order of the stack
        """
        self.items.reverse()


class Queue(Stack):
    """
    Encapsulates logic of a queue using Stack API
    """
    def __init__(self):
        """
        Default constructor
        """
        super(Queue, self).__init__()

    def pop(self):
        """
        Removes the next item from the queue
        """
        if len(self.items) == 0:
            return None
        return self.items.pop()

    def push(self, item):
        """
        Add as item to the queue
        """
        self.items.append(item)

    def copy(self):
        """
        Performs a deep copy of the queue
        """
        queue = Queue()
        for i in self.items:
            if i is None:
                continue
            cpy = copy.deepcopy(i)
            queue.push(i)
        return queue
