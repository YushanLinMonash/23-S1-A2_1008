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
        """
        The complexity of this function is O(1), as it performs a simple modulo operation and access to the key's character.
        """
        if self.level < len(key):
            return ord(key[self.level]) % (self.TABLE_SIZE - 1)
        return self.TABLE_SIZE - 1

    def __getitem__(self, key: K) -> V:
        """
        Get the value at a certain key

        :raises KeyError: when the key doesn't exist.
        """
        """
        The complexity of this function depends on the level of the hash table.
    - If the level is less than the length of the key, the complexity is O(1).
    - If the level is equal to the length of the key, the complexity is O(N), 
    where N is the number of elements in the sub-hash table.
    - If the level is greater than the length of the key, the complexity is O(N^M), 
    where N is the number of elements in the sub-hash table 
    and M is the difference between the level and the length of the key.
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
        """
        The complexity of this function depends on the level of the hash table.
    - If the level is less than the length of the key, the complexity is O(1).
    - If the level is equal to the length of the key, the complexity is O(N), 
    where N is the number of elements in the sub-hash table.
    - If the level is greater than the length of the key, the complexity is O(N^M), 
    where N is the number of elements in the sub-hash table 
    and M is the difference between the level and the length of the key.
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
        """
        The complexity of this function depends on the level of the hash table.
    - If the level is less than the length of the key, the complexity is O(1).
    - If the level is equal to the length of the key, the complexity is O(N),
     where N is the number of elements in the sub-hash table.
    - If the level is greater than the length of the key, the complexity is O(N^M),
     where N is the number of elements in the sub-hash table 
     and M is the difference between the level and the length of the key.
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
        """
        The complexity of this function is O(1), as it returns the count attribute.
        """
        return self.count

    def __str__(self) -> str:
        """
        String representation.

        Not required but may be a good testing tool.
        """
        """
        The complexity of this function depends on the number of elements in the hash table.
        In the worst case, it can be O(N), where N is the number of elements.
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
        """
        The complexity of this function depends on the level of the hash table.
    - If the level is less than the length of the key, the complexity is O(1).
    - If the level is equal to the length of the key, 
    the complexity is O(N), where N is the number of elements in the sub-hash table.
    - If the level is greater than the length of the key, the complexity is O(N^M), 
    where N is the number of elements in the sub-hash table 
    and M is the difference between the level and the length of the key.
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
        """
        The complexity of this function depends on the level of the hash which will be O(n)
        """
        try:
            _ = self[key]
        except KeyError:
            return False
        else:
            return True
