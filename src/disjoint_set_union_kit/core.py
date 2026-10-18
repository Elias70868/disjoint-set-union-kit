# Copyright 2024 disjoint-set-union-kit authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Disjoint Set Union data structure.

A union-find / disjoint-set-union implementation that tracks non-overlapping
sets of hashable elements. Supports adding elements dynamically, linking two
sets together, querying whether two elements share a set, and counting the
size of each set.

This implementation uses union-by-size (the larger set absorbs the smaller)
plus iterative path compression on find. Together these give amortised
near-constant time per operation; the inverse-Ackermann bound applies.

Design choices
--------------
* Elements may be any hashable Python object, not just integers. This is why
  we store parent and size in dicts rather than a pre-allocated array.
* ``union`` returns a boolean: True if a merge actually happened, False if the
  two elements were already in the same set (including the case where both
  sides are the same element). Returning False for a no-op keeps the call
  idempotent and lets callers treat the return value as "did anything change".
* ``same`` raises ``KeyError`` if either element is unknown rather than silently
  returning False. A silent False is ambiguous: it could mean "different sets"
  or "never seen this element". We refuse to guess.
"""

from __future__ import annotations

from typing import Hashable

__all__ = ["DisjointSetUnion", "DSU"]


class DisjointSetUnion:
    """Maintain a collection of non-overlapping sets with efficient union and find.

    Add elements with ``add`` or implicitly via ``union`` / ``find``. Link two
    sets with ``union``. Query the representative with ``find`` or check
    connectivity with ``same``. Get the size of a set with ``size``.

    Example::

        dsu = DisjointSetUnion()
        dsu.add(1)
        dsu.add(2)
        dsu.union(1, 2)
        assert dsu.same(1, 2)
        assert dsu.size(1) == 2
    """

    def __init__(self) -> None:
        # Each element maps to its parent. A root maps to itself.
        self._parent: dict[Hashable, Hashable] = {}
        # Only roots carry a meaningful size; this is maintained on union.
        self._size: dict[Hashable, int] = {}

    def __len__(self) -> int:
        """Number of distinct elements tracked, not number of sets."""
        return len(self._parent)

    def __contains__(self, item: object) -> bool:
        return item in self._parent

    def add(self, item: Hashable) -> bool:
        """Register a new singleton set.

        Returns True if the element was added, False if it already existed.
        Fails with TypeError for unhashable values (dict, list, etc.).
        """
        if item in self._parent:
            return False
        self._parent[item] = item
        self._size[item] = 1
        return True

    def find(self, item: Hashable) -> Hashable:
        """Return the representative element of the set containing ``item``.

        Which element becomes the representative is an internal detail (the
        larger set's root wins on union); do not rely on a specific value,
        only on the fact that two elements in the same set share a representative.

        Raises KeyError if ``item`` has never been added.
        """
        if item not in self._parent:
            raise KeyError(item)
        # Iterative path compression: walk to the root, then re-point every
        # node on the path directly at the root so future finds are O(1).
        path: list[Hashable] = []
        current = item
        while True:
            parent = self._parent[current]
            if parent == current:
                root = current
                break
            path.append(current)
            current = parent
        for node in path:
            self._parent[node] = root
        return root

    def union(self, a: Hashable, b: Hashable) -> bool:
        """Merge the sets containing ``a`` and ``b``.

        Returns True if two distinct sets were linked, False if they were
        already the same set (this includes ``a is b``).

        Either element not previously known is added automatically, mirroring
        ``add``. This makes a chain of ``union`` calls self-initialising.

        Raises TypeError if either argument is unhashable.
        """
        if a not in self._parent:
            self.add(a)
        if b not in self._parent:
            self.add(b)

        root_a = self.find(a)
        root_b = self.find(b)
        if root_a == root_b:
            return False

        # Union by size: attach the smaller tree under the larger one. This
        # keeps the worst-case tree depth logarithmic in the set size, which
        # bounds the find cost even before path compression kicks in.
        if self._size[root_a] < self._size[root_b]:
            root_a, root_b = root_b, root_a
        self._parent[root_b] = root_a
        self._size[root_a] += self._size[root_b]
        # root_b is no longer a root; its size entry is stale and unused. We
        # leave it in the dict rather than ``del`` so that a future re-add of
        # a previously-removed element (not currently supported) or a size
        # query on a stale root cannot raise KeyError unexpectedly. The size
        # of a non-root is never consulted by any code path.
        return True

    def same(self, a: Hashable, b: Hashable) -> bool:
        """True if ``a`` and ``b`` are in the same set, False if different sets.

        Raises KeyError if either element is unknown. We raise rather than
        return False so callers can distinguish "different sets" from
        "element never registered".
        """
        return self.find(a) == self.find(b)

    def size(self, item: Hashable) -> int:
        """Number of elements in the set containing ``item``.

        Raises KeyError if ``item`` is unknown.
        """
        root = self.find(item)
        return self._size[root]

    def num_sets(self) -> int:
        """Count of disjoint sets currently tracked.

        A root is an element whose parent is itself. Counting those gives the
        number of sets in O(n) over the element count.
        """
        return sum(1 for node, parent in self._parent.items() if node == parent)


# Short alias for users who type the name often.
DSU = DisjointSetUnion
