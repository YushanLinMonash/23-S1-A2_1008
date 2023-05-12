from mountain import Mountain
from algorithms.mergesort import mergesort


class MountainManager:

    def __init__(self) -> None:
        self.mountains = []

    def add_mountain(self, mountain: Mountain):
        """
        Time Complexity: O(1) (constant time),
        Appending an element to a list has a constant time complexity as it does not depend on the size of the list.
        The operation simply adds the element to the end of the list.
        """
        self.mountains.append(mountain)

    def remove_mountain(self, mountain: Mountain):
        """
        Time Complexity: O(n) (linear time)
        Removing an element from a list has a linear time complexity
        as it may require shifting all subsequent elements to fill the gap.
        The worst-case scenario occurs when the element to be removed is at the beginning of the list,
        requiring all other elements to be shifted.
        """
        self.mountains.remove(mountain)

    def edit_mountain(self, old: Mountain, new: Mountain):
        """
        Time Complexity: O(n) (linear time)
        Searching for the old mountain using index has a linear time complexity,
        as it may require traversing the entire list. After finding the index,
        updating the mountain has a constant time complexity.
        """
        index = self.mountains.index(old)
        self.mountains[index] = new

    def mountains_with_difficulty(self, diff: int):
        """
        Time Complexity: O(n) (linear time)
        The function iterates over all mountains in the list once,
        checking the difficulty level of each mountain.
        The time complexity is proportional to the number of mountains in the list.
        """
        mountains = []
        for m in self.mountains:
            if m.difficulty_level == diff:
                mountains.append(m)
        return mountains

    def group_by_difficulty(self):
        """
        O(n log n)
        merge sort
        """
        difficulties = []

        for m in self.mountains:
            if m.difficulty_level not in difficulties:
                difficulties.append(m.difficulty_level)

        sorted_difficulties = mergesort(difficulties)

        groupMountains = []

        for diff in sorted_difficulties:
            groupMountains.append(self.mountains_with_difficulty(diff))

        return groupMountains
