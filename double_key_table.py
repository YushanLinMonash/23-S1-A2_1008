from __future__ import annotations

from typing import Generic, TypeVar, Iterator
from data_structures.hash_table import LinearProbeTable, FullError
from data_structures.referential_array import ArrayR

K1 = TypeVar('K1')
K2 = TypeVar('K2')
V = TypeVar('V')


class DoubleKeyTable(Generic[K1, K2, V]):
    """
    Double Hash Table.

    Type Arguments:
        - K1:   1st Key Type. In most cases should be string.
                Otherwise `hash1` should be overwritten.
        - K2:   2nd Key Type. In most cases should be string.
                Otherwise `hash2` should be overwritten.
        - V:    Value Type.

    Unless stated otherwise, all methods have O(1) complexity.
    """

    # No test case should exceed 1 million entries.
    TABLE_SIZES = [5, 13, 29, 53, 97, 193, 389, 769, 1543, 3079, 6151, 12289, 24593, 49157, 98317, 196613, 393241,
                   786433, 1572869]

    HASH_BASE = 31

    def __init__(self, sizes: list | None = None, internal_sizes: list | None = None) -> None:
        """
        create the underlying array. If sizes is not None,
        the provided array should replace the existing TABLE_SIZES to decide the size of the top-level hash table.
        If internal_sizes is not None,
        the provided array should replace the existing TABLE_SIZES for the internal hash tables.
        """
        """
        The complexity of this function is O(1).
        The function initializes the DoubleKeyTable object by creating the underlying array based on the specified sizes.
        If the sizes argument is provided, it replaces the default TABLE_SIZES to determine the size of the top-level hash table.
        If the internal_sizes argument is provided, it replaces the default TABLE_SIZES for the internal hash tables.
        """
        if sizes is not None:
            self.TABLE_SIZES = sizes

        if internal_sizes is not None:
            internal_table_sizes = internal_sizes
        else:
            internal_table_sizes = self.TABLE_SIZES

        self.size_index = 0
        self.array: ArrayR[LinearProbeTable[K2, V]] = ArrayR(self.TABLE_SIZES[self.size_index])
        for i in range(self.TABLE_SIZES[self.size_index]):
            self.array[i] = LinearProbeTable(sizes=internal_table_sizes)
        self.count = 0

    def hash1(self, key: K1) -> int:
        """
        Hash the 1st key for insert/retrieve/update into the hashtable.

        :complexity: O(len(key))
        """
        key = str(key)
        value = 0
        a = 31415
        for char in key:
            value = (ord(char) + a * value) % self.table_size
            a = a * self.HASH_BASE % (self.table_size - 1)
        return value

    def hash2(self, key: K2, sub_table: LinearProbeTable[K2, V]) -> int:
        """
        Hash the 2nd key for insert/retrieve/update into the hashtable.

        :complexity: O(len(key))
        """
        key = str(key)
        value = 0
        a = 31415
        for char in key:
            value = (ord(char) + a * value) % sub_table.table_size
            a = a * self.HASH_BASE % (sub_table.table_size - 1)
        return value

    def _linear_probe(self, key1: K1, key2: K2, is_insert: bool) -> tuple[int, int]:
        """
        Find the correct position for this key in the hash table using linear probing.

        :raises KeyError: When the key pair is not in the table, but is_insert is False.
        :raises FullError: When a table is full and cannot be inserted.

        return the:
        Index to access in the top-level table, followed by
        Index to access in the low-level table
        In a tuple.
        """
        """
        The complexity of this function depends on the number of probing iterations required.
        In the worst case, it can be O(N^2), where N is the number of elements in the hash table.
        This occurs when the table is full and probing continues until an empty slot is found.
        """
        position1 = self.hash1(key1)
        internal_table = self.array[position1]

        if is_insert and internal_table.is_empty():
            internal_table = LinearProbeTable(sizes=self.TABLE_SIZES)
            self.array[position1] = internal_table

        position2 = self.hash2(key2, internal_table)

        for _ in range(internal_table.table_size):
            if internal_table.array[position2] is None:
                if is_insert:
                    return position1, position2
                else:
                    raise KeyError((key1, key2))
            elif internal_table.array[position2][0] == key2:
                return position1, position2
            else:
                position2 = (position2 + 1) % internal_table.table_size

        if is_insert:
            raise FullError("is full")
        else:
            raise KeyError((key1, key2))

    def iter_keys(self, key: K1 | None = None) -> Iterator[K1 | K2]:
        """
        key = None: returns an iterator of all top-level keys in the table.
        key = x: returns an iterator of all bottom-level keys for top-level key x.
        """
        """
        The complexity of this function is O(N), where N is the number of elements in the hash table.
        It iterates over the top-level keys or bottom-level keys, depending on the value of the key parameter.
        """
        if key is None:
            for key1, internal_table in enumerate(self.array):
                if not internal_table.is_empty():
                    yield key1
        else:
            position = self.hash1(key)
            internal_table = self.array[position]
            for key2 in internal_table.keys():
                yield key2

    def keys(self, key: K1 | None = None) -> list[K1]:
        """
        key = None: returns all top-level keys in the table.
        key = x: returns all bottom-level keys for top-level key x.
        """
        """
        The complexity of this function is O(N), where N is the number of elements in the hash table.
        It iterates over the top-level keys or bottom-level keys, depending on the value of the key parameter.
        """
        if key is None:
            return [key1 for key1, internal_table in enumerate(self.array) if not internal_table.is_empty()]
        else:
            position = self.hash1(key)
            internal_table = self.array[position]
            return list(internal_table.keys())

    def iter_values(self, key: K1 | None = None) -> Iterator[V]:
        """
        key = None:
            Returns an iterator of all values in hash table
        key = k:
            Returns an iterator of all values in the bottom-hash-table for k.
        """
        """
        The complexity of this function is O(N), where N is the number of elements in the hash table.
        It iterates over all values in the hash table or the values associated with a specific top-level key.
        """
        if key is None:
            for internal_table in self.array:
                if not internal_table.is_empty():
                    for value in internal_table.values():
                        yield value
        else:
            position = self.hash1(key)
            internal_table = self.array[position]
            for value in internal_table.values():
                yield value

    def values(self, key: K1 | None = None) -> list[V]:
        """
        key = None: returns all values in the table.
        key = x: returns all values for top-level key x.
        """
        """
        The complexity of this function is O(N), where N is the number of elements in the hash table.
        It returns a list of all values in the hash table or the values associated with a specific top-level key.
        """
        result = []
        if key is None:
            for internal_table in self.array:
                if not internal_table.is_empty():
                    result.extend(internal_table.values())
        else:
            position = self.hash1(key)
            internal_table = self.array[position]
            result.extend(internal_table.values())
        return result

    def __contains__(self, key: tuple[K1, K2]) -> bool:
        """
        Checks to see if the given key is in the Hash Table

        :complexity: See linear probe.
        """
        """
        The complexity of this function depends on the _linear_probe function, which can be O(N^2) in the worst case.
        It checks if a given key pair is in the hash table.
        """
        key1, key2 = key
        position = self.hash1(key1)
        internal_table = self.array[position]
        return key2 in internal_table

    def __getitem__(self, key: tuple[K1, K2]) -> V:
        """
        Get the value at a certain key

        :raises KeyError: when the key doesn't exist.
        """
        """
        The complexity of this function depends on the _linear_probe function, which can be O(N^2) in the worst case.
        It retrieves the value associated with a given key pair from the hash table.
        """
        key1, key2 = key
        position = self.hash1(key1)
        internal_table = self.array[position]
        return internal_table[key2]

    def __setitem__(self, key: tuple[K1, K2], data: V) -> None:
        """
        Set an (key, value) pair in our hash table.
        """
        """
        The complexity of this function depends on the _linear_probe function, which can be O(N^2) in the worst case.
        It sets a key-value pair in the hash table.
        """
        key1, key2 = key
        position = self.hash1(key1)
        internal_table = self.array[position]
        internal_table[key2] = data

    def __delitem__(self, key: tuple[K1, K2]) -> None:
        """
        Deletes a (key, value) pair in our hash table.

        :raises KeyError: when the key doesn't exist.
        """
        """
        The complexity of this function depends on the _linear_probe function, which can be O(N^2) in the worst case.
        It deletes a key-value pair from the hash table.
        """
        key1, key2 = key
        position = self.hash1(key1)
        internal_table = self.array[position]
        del internal_table[key2]
        if len(internal_table) == 0:
            self.array[position] = LinearProbeTable(sizes=self.TABLE_SIZES)

    def _rehash(self) -> None:
        """
        Need to resize table and reinsert all values

        :complexity best: O(N*hash(K)) No probing.
        :complexity worst: O(N*hash(K) + N^2*comp(K)) Lots of probing.
        Where N is len(self)
        """
        old_array = self.array
        self.size_index += 1

        # Create a new array with the doubled size
        self.array = ArrayR(self.TABLE_SIZES[self.size_index])
        for i in range(self.TABLE_SIZES[self.size_index]):
            self.array[i] = LinearProbeTable(sizes=self.TABLE_SIZES)

        # Reinsert key-value pairs into the new array
        for internal_table in old_array:
            for key2, value in internal_table.items():
                key1 = self.iter_keys().__next__()
                self[key1, key2] = value

    def table_size(self) -> int:
        """
        Return the current size of the table (different from the length)
        """
        return self.TABLE_SIZES[self.size_index]

    def __len__(self) -> int:
        """
        Returns number of elements in the hash table
        """
        total_length = 0
        for internal_table in self.array:
            total_length += len(internal_table)
        return total_length

    def __str__(self) -> str:
        """
        String representation.

        Not required but may be a good testing tool.
        """
        raise NotImplementedError()
