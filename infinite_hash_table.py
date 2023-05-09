from __future__ import annotations
from typing import Generic, TypeVar

from data_structures.referential_array import ArrayR

K = TypeVar("K")
V = TypeVar("V")


class InfiniteHashTable(Generic[K, V]):
    """
    Infinite Hash Table.

    Type Arguments:
        - K:    Key Type. In most cases should be string.
                Otherwise `hash` should be overwritten.
        - V:    Value Type.

    Unless stated otherwise, all methods have O(1) complexity.
    """

    TABLE_SIZE = 27

    def __init__(self, level: int = 0) -> None:
        self.array = ArrayR(self.TABLE_SIZE)
        self.level = level
        self.count = 0

    def hash(self, key: K) -> int:
        if self.level < len(key):
            return ord(key[self.level]) % (self.TABLE_SIZE - 1)
        return self.TABLE_SIZE - 1

    def __getitem__(self, key: K) -> V:
        """
        Get the value at a certain key

        :raises KeyError: when the key doesn't exist.
        """
        index = self.hash(key)
        entry = self.array[index]

        if entry is None:
            raise KeyError('unfounded')

        if isinstance(entry, tuple):
            if entry[0] == key:
                return entry[1]
            else:
                raise KeyError('unfounded')

        return entry[key]

    def __setitem__(self, key: K, value: V) -> None:
        """
        Set an (key, value) pair in our hash table.
        """
        index = self.hash(key)
        entry = self.array[index]

        if entry is None:
            self.array[index] = (key, value)
            self.count += 1
        elif isinstance(entry, tuple):
            if entry[0] == key:
                self.array[index] = (key, value)
            else:
                new_table = InfiniteHashTable(self.level + 1)
                new_table[entry[0]] = entry[1]
                new_table[key] = value
                self.array[index] = new_table
        else:
            entry[key] = value

    def __delitem__(self, key: K) -> None:
        """
        Deletes a (key, value) pair in our hash table.

        :raises KeyError: when the key doesn't exist.
        """
        index = self.hash(key)
        entry = self.array[index]

        if entry is None:
            raise KeyError('unfounded')

        if isinstance(entry, tuple):
            if entry[0] == key:
                self.array[index] = None
                self.count -= 1
            else:
                raise KeyError('unfounded')
        else:
            del entry[key]
            if len(entry) == 1:
                k, v = next(iter(entry.array))
                self.array[index] = (k, v)

    def __len__(self):
        return self.count

    def __str__(self) -> str:
        """
        String representation.

        Not required but may be a good testing tool.
        """
        result = []
        for entry in self.array:
            if entry is not None:
                if isinstance(entry, tuple):
                    result.append(f'({entry[0]}, {entry[1]})')
                else:
                    result.append(str(entry))
        return f'[{", ".join(result)}]'

    def get_location(self, key):
        """
        Get the sequence of positions required to access this key.

        :raises KeyError: when the key doesn't exist.
        """
        location = [self.hash(key)]
        entry = self.array[location[0]]

        if entry is None:
            raise KeyError('unfounded')

        if isinstance(entry, tuple):
            if entry[0] == key:
                return location
            else:
                raise KeyError('unfounded')
        else:
            while not isinstance(entry, tuple) or entry[0] != key:
                sub_location = entry.get_location(key)
                location.extend(sub_location)
                entry = entry.array[sub_location[-1]]

            return location

    def __contains__(self, key: K) -> bool:
        """
        Checks to see if the given key is in the Hash Table

        :complexity: See linear probe.
        """
        try:
            _ = self[key]
        except KeyError:
            return False
        else:
            return True
