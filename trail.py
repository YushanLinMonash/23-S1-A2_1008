from __future__ import annotations
from dataclasses import dataclass

from data_structures.stack_adt import Stack
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
        """Follow a path and add mountains according to a personality."""
        stack = Stack[Trail]()
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
        stack = Stack[Trail]()
        stack.push(self)
        mountains = []

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

    def length_k_paths(self, k) -> list[list[Mountain]]:  # Input to this should not exceed k > 50, at most 5 branches.
        """
        Returns a list of all paths of containing exactly k mountains.
        Paths are represented as lists of mountains.

        Paths are unique if they take a different branch, even if this results in the same set of mountains.
        """
        stack = Stack[tuple[Trail, list[Mountain]]]()
        stack.push((self, []))
        paths = []

        while not stack.is_empty():
            current_trail, current_mountains = stack.pop()
            current_store = current_trail.store

            if isinstance(current_store, TrailSeries):
                new_mountains = current_mountains + [current_store.mountain]
                if len(new_mountains) == k:
                    paths.append(new_mountains)
                else:
                    stack.push((current_store.following, new_mountains))
            elif isinstance(current_store, TrailSplit):
                stack.push((current_store.path_top, current_mountains))
                stack.push((current_store.path_bottom, current_mountains))

        return paths
