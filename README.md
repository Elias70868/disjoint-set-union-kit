# disjoint-set-union-kit

A small, dependency-free Python implementation of the disjoint-set-union (union-find) data structure. It tracks non-overlapping sets of hashable elements and supports efficient `union`, `find`, and connectivity queries with union-by-size and path compression.

```python
from disjoint_set_union_kit import DSU

dsu = DSU()
dsu.add(1)
dsu.add(2)
assert dsu.union(1, 2) is True   # sets merged
assert dsu.union(1, 2) is False   # already same set, no-op
assert dsu.same(1, 2) is True
assert dsu.size(1) == 2
assert dsu.num_sets() == 1
```

The exported names are `DisjointSetUnion` and its short alias `DSU` (both from `disjoint_set_union_kit`).

## Why this exists

Graph and clustering code often needs to answer "are these two nodes in the same component?" and "merge these two components" repeatedly, fast. A dict-backed union-find gives you that without pulling in a graph library or hand-rolling a class each time. The trade-off versus an array-backed implementation is that elements can be any hashable Python object (strings, tuples, mixed types) rather than contiguous integers, at the cost of dict lookups instead of array indexing.

## The awkward edge

`same` and `find` raise `KeyError` if you pass an element that was never added. This is deliberate: a silent `False` from `same` is ambiguous between "these are in different sets" and "you never registered this element." Raising forces you to call `add` or rely on `union`'s auto-add behaviour. If you want a lenient check, guard with `item in dsu` first.

`union` auto-adds unknown elements on both sides, so a chain of `union` calls is self-initialising. `union(a, a)` returns `False` (same set, no change).

Which element becomes a set's representative is an internal detail (the larger set's root wins on merge); rely only on `same` and `find` for equality, not on the specific representative value.

## Running the tests

```bash
PYTHONPATH=src python -m unittest discover -s tests
```

## Performance

The window keeps a bounded buffer, so `push` is constant time and memory does not
grow with the length of the stream. `peak` and `trough` are linear in the window
size, which is the trade that keeps `push` cheap.

