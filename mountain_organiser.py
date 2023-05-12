from __future__ import annotations
from algorithms.binary_search import binary_search
from data_structures.referential_array import ArrayR
from mountain import Mountain


class MountainOrganiser:

    def __init__(self) -> None:
        """
        Time Complexity: O(1) (constant time)
        Initializing the self.mountains array with length 1 and setting the self.
        length variable both have constant time complexity.
        """
        self.mountains = ArrayR[Mountain](1)
        self.length = 0

    def cur_position(self, mountain: Mountain) -> int:
        """
        Time Complexity: O(log n) (logarithmic time)
        The function performs a binary search on the self.mountains array,
        which has a length of self.length.
        Binary search has a time complexity of O(log n) as it divides the search space in half at each step.
        """
        index = binary_search(self.mountains[:self.length], mountain)
        if index < self.length and self.mountains[index] == mountain:
            return index
        else:
            raise KeyError('not found')

    def add_mountains(self, mountains: list[Mountain]) -> None:
        raise NotImplementedError()