from __future__ import annotations
from dataclasses import dataclass

from data_structures.stack_adt import Stack, T
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
        return self.following.store

    def add_mountain_before(self, mountain: Mountain) -> TrailStore:
        """Adds a mountain in series before the current one."""
        return TrailSeries(mountain, Trail(self))

    def add_empty_branch_before(self) -> TrailStore:
        """Adds an empty branch, where the current trailstore is now the following path."""
        return TrailSplit(Trail(None), Trail(None), Trail(self))

    def add_mountain_after(self, mountain: Mountain) -> TrailStore:
        """Adds a mountain after the current mountain, but before the following trail."""
        return TrailSeries(self.mountain, Trail(TrailSeries(mountain, self.following)))

    def add_empty_branch_after(self) -> TrailStore:
        """Adds an empty branch after the current mountain, but before the following trail."""
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
        return Trail(TrailSeries(mountain, self))

    def add_empty_branch_before(self) -> Trail:
        """Adds an empty branch before everything currently in the trail."""
        return Trail(TrailSplit(Trail(None), Trail(None), self))

    def follow_path(self, personality: WalkerPersonality) -> None:
        stack = ArrayStack()
        stack.push((self, False))

        while not stack.is_empty():
            current_trail, visited = stack.pop()
            current_store = current_trail.store

            if isinstance(current_store, TrailSeries):
                if not visited:
                    stack.push((current_trail, True))
                    personality.add_mountain(current_store.mountain)
                    stack.push((current_store.following, False))
                else:
                    continue
            elif isinstance(current_store, TrailSplit):
                if not visited:
                    stack.push((current_trail, True))
                    if personality.select_branch(current_store.path_top, current_store.path_bottom):
                        stack.push((current_store.path_top, False))
                    else:
                        stack.push((current_store.path_bottom, False))

    def collect_all_mountains(self) -> list[Mountain]:
        """Returns a list of all mountains on the trail."""
        raise NotImplementedError()

    def length_k_paths(self, k) -> list[list[Mountain]]:  # Input to this should not exceed k > 50, at most 5 branches.
        """
        Returns a list of all paths of containing exactly k mountains.
        Paths are represented as lists of mountains.

        Paths are unique if they take a different branch, even if this results in the same set of mountains.
        """
        raise NotImplementedError()
