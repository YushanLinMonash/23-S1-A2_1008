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
    TABLE_SIZES = [5, 13, 29, 53, 97, 193, 389, 769, 1543, 3079, 6151, 12289, 24593, 49157, 98317, 196613, 393241, 786433, 1572869]

    HASH_BASE = 31

    def __init__(self, sizes:list|None=None, internal_sizes:list|None=None) -> None:
        """
        create the underlying array. If sizes is not None,
        the provided array should replace the existing TABLE_SIZES to decide the size of the top-level hash table.
        If internal_sizes is not None,
        the provided array should replace the existing TABLE_SIZES for the internal hash tables.
        """
        if sizes is None:
            self.table_sizes = self.TABLE_SIZES
        else:
            self.table_sizes = sizes

        if internal_sizes is None:
            self.internal_sizes = self.TABLE_SIZES
        else:
            self.internal_sizes = internal_sizes

        self.table_size = self.table_sizes[0]
        self.array = ArrayR[LinearProbeTable](self.table_size)
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
        index1 = self.hash1(key1)
        sub_table = self.array[index1]

        if sub_table is None:
            if is_insert:
                sub_table = LinearProbeTable(self.internal_sizes)
                self.array[index1] = sub_table
            else:
                return -1, -1

        index2 = self.hash2(key2, sub_table)
        if is_insert:
            if sub_table[index2] is None:
                sub_table[index2] = key2
            else:
                raise FullError("Table is full and cannot be inserted.")
        else:
            if sub_table[index2] is None:
                return -1, -1

        return index1, index2

    def iter_keys(self, key:K1|None=None) -> Iterator[K1|K2]:
        """
        key = None:
            Returns an iterator of all top-level keys in hash table
        key = k:
            Returns an iterator of all keys in the bottom-hash-table for k.
        """
        if key is None:
            for sub_table in self.table:
                if sub_table is not None:
                    yield sub_table.key
        else:
            i = self.hash1(key)
            sub_table = self.table[i]
            if sub_table is not None:
                for j, entry in enumerate(sub_table.table):
                    if entry is not None:
                        yield entry.key

    def keys(self, key:K1|None=None) -> list[K1]:
        """
        key = None: returns all top-level keys in the table.
        key = x: returns all bottom-level keys for top-level key x.
        """
        return list(self.iter_keys(key))

    def iter_values(self, key:K1|None=None) -> Iterator[V]:
        """
        key = None:
            Returns an iterator of all values in hash table
        key = k:
            Returns an iterator of all values in the bottom-hash-table for k.
        """
        if key is None:
            for sub_table in self.table:
                if sub_table is not None:
                    for entry in sub_table.table:
                        if entry is not None:
                            yield entry.value
        else:
            i = self.hash1(key)
            sub_table = self.table[i]
            if sub_table is not None:
                for entry in sub_table.table:
                    if entry is not None:
                        yield entry.value


    def values(self, key:K1|None=None) -> list[V]:
        """
        key = None: returns all values in the table.
        key = x: returns all values for top-level key x.
        """
        return list(self.iter_values(key))

    def __contains__(self, key: tuple[K1, K2]) -> bool:
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

    def __getitem__(self, key: tuple[K1, K2]) -> V:
        """
        Get the value at a certain key

        :raises KeyError: when the key doesn't exist.
        """
        index1, index2 = self._linear_probe(key[0], key[1], False)
        return self.array[index1][index2]

    def __setitem__(self, key: tuple[K1, K2], data: V) -> None:
        """
        Set an (key, value) pair in our hash table.
        """
        index1, index2 = self._linear_probe(key[0], key[1], True)
        self.array[index1][index2] = data
        self.count += 1


    def __delitem__(self, key: tuple[K1, K2]) -> None:
        """
        Deletes a (key, value) pair in our hash table.

        :raises KeyError: when the key doesn't exist.
        """
        index1, index2 = self._linear_probe(key[0], key[1], False)
        self.array[index1].delete(index2)
        self.count -= 1

    def _rehash(self) -> None:
        """
        Need to resize table and reinsert all values

        :complexity best: O(N*hash(K)) No probing.
        :complexity worst: O(N*hash(K) + N^2*comp(K)) Lots of probing.
        Where N is len(self)
        """
        old_array = self.array
        old_table_size = self.table_size
        self.table_size = self.table_sizes[self.table_sizes.index(old_table_size) + 1]
        self.array = ArrayR[LinearProbeTable](self.table_size)

        for sub_table in old_array:
            if sub_table is not None:
                for entry in sub_table.table:
                    if entry is not None:
                        self[entry.key] = entry.value

    def table_size(self) -> int:
        """
        Return the current size of the table (different from the length)
        """
        return self.table_size

    def __len__(self) -> int:
        """
        Returns number of elements in the hash table
        """
        raise NotImplementedError()

    def __str__(self) -> str:
        """
        String representation.

        Not required but may be a good testing tool.
        """
        raise NotImplementedError()
