from __future__ import annotations
from dataclasses import dataclass

from data_structures.stack_adt import Stack, T
from data_structures.linked_stack import LinkedStack
from mountain import Mountain

from typing import TYPE_CHECKING, Union

# Avoid circular imports for typing.
if TYPE_CHECKING:
    from personality import WalkerPersonality


@dataclass
class TrailSplit:
    """
    A split in the trail.
       ___path_top____
      /               \
    -<                 >-path_follow-
      \__path_bottom__/
    """

    path_top: Trail
    path_bottom: Trail
    path_follow: Trail

    def remove_branch(self) -> TrailStore:
        """Removes the branch, should just leave the remaining following trail."""
        """
        Time Complexity: O(1) (constant time)
        The function simply returns the path_follow attribute of the TrailSplit object, 
        which is a constant-time operation.
        """
        return self.path_follow.store


@dataclass
class TrailSeries:
    """
    A mountain, followed by the rest of the trail

    --mountain--following--

    """

    mountain: Mountain
    following: Trail

    def remove_mountain(self) -> TrailStore:
        """Removes the mountain at the beginning of this series."""
        """
        Time Complexity: O(1) (constant time)
        The function simply returns the following attribute of the TrailSeries object, 
        which is a constant-time operation.
        """
        return self.following.store

    def add_mountain_before(self, mountain: Mountain) -> TrailStore:
        """Adds a mountain in series before the current one."""
        """
        Time Complexity: O(1) (constant time)
        The function creates a new TrailSeries object with the provided mountain added before the current mountain. 
        It involves creating a new object, but it does not depend on the size of the existing trail.
        """
        return TrailSeries(mountain, Trail(self))

    def add_empty_branch_before(self) -> TrailStore:
        """Adds an empty branch, where the current trailstore is now the following path."""
        """
        Time Complexity: O(1) (constant time)
        The function creates a new TrailSplit object with an empty branch before the current trail. 
        It involves creating a new object, but it does not depend on the size of the existing trail.
        """
        return TrailSplit(Trail(None), Trail(None), Trail(self))

    def add_mountain_after(self, mountain: Mountain) -> TrailStore:
        """Adds a mountain after the current mountain, but before the following trail."""
        """
        Time Complexity: O(1) (constant time)
        The function creates a new TrailSeries object with the provided mountain added after the current mountain. 
        It involves creating a new object, but it does not depend on the size of the existing trail.
        """
        return TrailSeries(self.mountain, Trail(TrailSeries(mountain, self.following)))

    def add_empty_branch_after(self) -> TrailStore:
        """Adds an empty branch after the current mountain, but before the following trail."""
        """
        Time Complexity: O(1) (constant time)
        The function creates a new TrailSeries object with an empty branch after the current mountain. 
        It involves creating a new object, but it does not depend on the size of the existing trail.
        """
        return TrailSeries(self.mountain, Trail(TrailSplit(Trail(None), Trail(None), self.following)))


TrailStore = Union[TrailSplit, TrailSeries, None]


class ArrayStack(Stack[T]):
    def __init__(self) -> None:
        super().__init__()
        self.items = []

    def push(self, item: T) -> None:
        self.items.append(item)
        self.length += 1

    def pop(self) -> T:
        if self.is_empty():
            raise IndexError("Pop from an empty stack")
        item = self.items.pop()
        self.length -= 1
        return item

    def peek(self) -> T:
        if self.is_empty():
            raise IndexError("Peek at an empty stack")
        return self.items[-1]

    def is_full(self) -> bool:
        return False


@dataclass
class Trail:
    store: TrailStore = None

    def add_mountain_before(self, mountain: Mountain) -> Trail:
        """Adds a mountain before everything currently in the trail."""
        """
        Time Complexity: O(1) (constant time)
        The function creates a new Trail object with the provided mountain added before the current trail. 
        It involves creating a new object, but it does not depend on the size of the existing trail.
        """
        return Trail(TrailSeries(mountain, self))

    def add_empty_branch_before(self) -> Trail:
        """Adds an empty branch before everything currently in the trail."""
        """
        Time Complexity: O(1) (constant time)
        The function creates a new Trail object with an empty branch before the current trail. It involves creating a new object, but it does not depend on the size of the existing trail.
        """
        return Trail(TrailSplit(Trail(None), Trail(None), self))

    def follow_path(self, personality: WalkerPersonality) -> None:
        """
        Time Complexity: O(n) (linear time)
        The function uses a stack to iterate through the trail.
        It visits each node in the trail once,
        so the time complexity is linear with respect to the size of the trail.
        """
        stack = ArrayStack()
        stack.push(self)

        while not stack.is_empty():
            current_trail = stack.pop()
            current_store = current_trail.store

            if isinstance(current_store, TrailSeries):
                personality.add_mountain(current_store.mountain)
                stack.push(current_store.following)
            elif isinstance(current_store, TrailSplit):
                if personality.select_branch(current_store.path_top, current_store.path_bottom):
                    stack.push(current_store.path_top)
                else:
                    stack.push(current_store.path_bottom)

    def collect_all_mountains(self) -> list[Mountain]:
        """Returns a list of all mountains on the trail."""
        """
        Time Complexity: O(n) (linear time)
        The function uses a stack to iterate through the trail. 
        It visits each node in the trail once and appends the mountains to the mountains list, 
        resulting in linear time complexity.
        """
        mountains = []
        stack = ArrayStack()
        stack.push(self)

        while not stack.is_empty():
            current_trail = stack.pop()
            current_store = current_trail.store

            if isinstance(current_store, TrailSeries):
                mountains.append(current_store.mountain)
                stack.push(current_store.following)
            elif isinstance(current_store, TrailSplit):
                stack.push(current_store.path_top)
                stack.push(current_store.path_bottom)

        return mountains

    def length_k_paths(self, k) -> list[list[Mountain]]:.
        """
        Returns a list of all paths of containing exactly k mountains.
        Paths are represented as lists of mountains.

        Paths are unique if they take a different branch, even if this results in the same set of mountains.
        """
        """
        O(b^k) (exponential time), where b is the maximum number of branches per split
        """
        paths = []
        stack = ArrayStack()
        stack.push((self, [], 0))

        while not stack.is_empty():
            current_trail, current_path, mountains_visited = stack.pop()
            current_store = current_trail.store

            if isinstance(current_store, TrailSeries):
                if current_store.mountain is not None:
                    path_new = current_path + [current_store.mountain]
                    visited_new = mountains_visited + 1
                else:
                    path_new = current_path
                    visited_new = mountains_visited

                if visited_new == k:
                    paths.append(path_new)
                else:
                    stack.push((current_store.following, path_new, visited_new))
            elif isinstance(current_store, TrailSplit):
                stack.push((current_store.path_top, current_path, mountains_visited))
                stack.push((current_store.path_bottom, current_path, mountains_visited))

        return paths
