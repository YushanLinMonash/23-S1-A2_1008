from __future__ import annotations
from algorithms.binary_search import binary_search
from data_structures.referential_array import ArrayR
from mountain import Mountain


class MountainOrganiser:

    def __init__(self) -> None:
        self.mountains = ArrayR[Mountain](1)
        self.length = 0

    def cur_position(self, mountain: Mountain) -> int:
        index = binary_search(self.mountains[:self.length], mountain)
        if index < self.length and self.mountains[index] == mountain:
            return index
        else:
            raise KeyError('not found')

    def add_mountains(self, mountains: list[Mountain]) -> None:
        mountains.sort(key=lambda m: (m.difficulty_level, m.length, m.name))

        new_array = ArrayR[Mountain](self.length + len(mountains))
        i, j, k = 0, 0, 0

        while i < self.length and j < len(mountains):
            if (self.mountains[i].difficulty_level < mountains[j].difficulty_level or
                    (self.mountains[i].difficulty_level == mountains[j].difficulty_level and
                     self.mountains[i].length < mountains[j].length) or
                    (self.mountains[i].difficulty_level == mountains[j].difficulty_level and
                     self.mountains[i].length == mountains[j].length and
                     self.mountains[i].name < mountains[j].name)):
                new_array[k] = self.mountains[i]
                i += 1
            else:
                new_array[k] = mountains[j]
                j += 1
            k += 1

        while i < self.length:
            new_array[k] = self.mountains[i]
            i += 1
            k += 1

        while j < len(mountains):
            new_array[k] = mountains[j]
            j += 1
            k += 1

        self.mountains = new_array
        self.length += len(mountains)