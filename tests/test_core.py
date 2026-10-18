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
"""Tests for disjoint_set_union_kit.core."""

import unittest

from disjoint_set_union_kit import DSU, DisjointSetUnion
from disjoint_set_union_kit.core import DSU as CoreDSU
from disjoint_set_union_kit.core import DisjointSetUnion as CoreDisjointSetUnion


class TestAddAndBasics(unittest.TestCase):
    def test_add_new_returns_true(self):
        dsu = DisjointSetUnion()
        self.assertTrue(dsu.add(1))

    def test_add_existing_returns_false(self):
        dsu = DisjointSetUnion()
        dsu.add(1)
        self.assertFalse(dsu.add(1))

    def test_len_counts_elements_not_sets(self):
        dsu = DisjointSetUnion()
        dsu.add(1)
        dsu.add(2)
        dsu.add(3)
        dsu.union(1, 2)
        self.assertEqual(len(dsu), 3)

    def test_contains(self):
        dsu = DisjointSetUnion()
        dsu.add(1)
        self.assertIn(1, dsu)
        self.assertNotIn(2, dsu)

    def test_num_sets_empty(self):
        self.assertEqual(DisjointSetUnion().num_sets(), 0)

    def test_num_sets_after_adds(self):
        dsu = DisjointSetUnion()
        dsu.add(1)
        dsu.add(2)
        dsu.add(3)
        self.assertEqual(dsu.num_sets(), 3)

    def test_num_sets_after_union(self):
        dsu = DisjointSetUnion()
        dsu.add(1)
        dsu.add(2)
        dsu.add(3)
        dsu.union(1, 2)
        self.assertEqual(dsu.num_sets(), 2)


class TestFind(unittest.TestCase):
    def test_find_singleton(self):
        dsu = DisjointSetUnion()
        dsu.add(1)
        self.assertEqual(dsu.find(1), 1)

    def test_find_unknown_raises_keyerror(self):
        dsu = DisjointSetUnion()
        with self.assertRaises(KeyError):
            dsu.find(1)

    def test_find_after_union_same_root(self):
        dsu = DisjointSetUnion()
        dsu.add(1)
        dsu.add(2)
        dsu.union(1, 2)
        self.assertEqual(dsu.find(1), dsu.find(2))

    def test_find_idempotent_after_path_compression(self):
        dsu = DisjointSetUnion()
        for i in range(10):
            dsu.add(i)
        for i in range(1, 10):
            dsu.union(0, i)
        first = dsu.find(9)
        second = dsu.find(9)
        self.assertEqual(first, second)


class TestUnion(unittest.TestCase):
    def test_union_distinct_returns_true(self):
        dsu = DisjointSetUnion()
        dsu.add(1)
        dsu.add(2)
        self.assertTrue(dsu.union(1, 2))

    def test_union_same_set_returns_false(self):
        dsu = DisjointSetUnion()
        dsu.add(1)
        dsu.add(2)
        dsu.union(1, 2)
        self.assertFalse(dsu.union(1, 2))

    def test_union_same_element_returns_false(self):
        dsu = DisjointSetUnion()
        dsu.add(1)
        self.assertFalse(dsu.union(1, 1))

    def test_union_auto_adds_unknown_elements(self):
        dsu = DisjointSetUnion()
        self.assertTrue(dsu.union(1, 2))
        self.assertIn(1, dsu)
        self.assertIn(2, dsu)
        self.assertTrue(dsu.same(1, 2))

    def test_union_one_known_one_unknown(self):
        dsu = DisjointSetUnion()
        dsu.add(1)
        self.assertTrue(dsu.union(1, 99))
        self.assertTrue(dsu.same(1, 99))

    def test_union_chain_makes_all_same_set(self):
        dsu = DisjointSetUnion()
        dsu.union(1, 2)
        dsu.union(3, 4)
        dsu.union(2, 3)
        for a in (1, 2, 3, 4):
            for b in (1, 2, 3, 4):
                self.assertTrue(dsu.same(a, b), f"{a} and {b} should be connected")
        self.assertEqual(dsu.size(1), 4)

    def test_union_does_not_cross_unrelated_sets(self):
        dsu = DisjointSetUnion()
        dsu.union(1, 2)
        dsu.union(3, 4)
        self.assertFalse(dsu.same(1, 3))
        self.assertFalse(dsu.same(2, 4))
        self.assertEqual(dsu.num_sets(), 2)

    def test_union_by_size_root_stability(self):
        """Union of a large set with a small set keeps the large set's root."""
        dsu = DisjointSetUnion()
        for i in range(5):
            dsu.add(i)
        dsu.union(0, 1)
        dsu.union(0, 2)  # set {0,1,2}, root is 0 (size 3)
        dsu.union(3, 4)  # set {3,4}, root is 3 (size 2)
        root_large = dsu.find(0)
        dsu.union(0, 3)  # large absorbs small
        self.assertEqual(dsu.find(3), root_large)
        self.assertEqual(dsu.find(4), root_large)


class TestSame(unittest.TestCase):
    def test_same_unknown_raises_keyerror(self):
        dsu = DisjointSetUnion()
        with self.assertRaises(KeyError):
            dsu.same(1, 2)

    def test_same_one_unknown_raises_keyerror(self):
        dsu = DisjointSetUnion()
        dsu.add(1)
        with self.assertRaises(KeyError):
            dsu.same(1, 2)

    def test_same_different_sets_returns_false(self):
        dsu = DisjointSetUnion()
        dsu.add(1)
        dsu.add(2)
        self.assertFalse(dsu.same(1, 2))


class TestSize(unittest.TestCase):
    def test_size_singleton(self):
        dsu = DisjointSetUnion()
        dsu.add(1)
        self.assertEqual(dsu.size(1), 1)

    def test_size_after_union(self):
        dsu = DisjointSetUnion()
        dsu.union(1, 2)
        dsu.union(3, 4)
        dsu.union(1, 3)
        self.assertEqual(dsu.size(1), 4)
        self.assertEqual(dsu.size(2), 4)
        self.assertEqual(dsu.size(3), 4)
        self.assertEqual(dsu.size(4), 4)

    def test_size_unknown_raises_keyerror(self):
        dsu = DisjointSetUnion()
        with self.assertRaises(KeyError):
            dsu.size(1)


class TestHashableNonIntElements(unittest.TestCase):
    def test_strings(self):
        dsu = DisjointSetUnion()
        dsu.add("alpha")
        dsu.add("beta")
        dsu.union("alpha", "beta")
        self.assertTrue(dsu.same("alpha", "beta"))
        self.assertEqual(dsu.size("alpha"), 2)

    def test_tuples(self):
        dsu = DisjointSetUnion()
        dsu.add((1, 2))
        dsu.add((3, 4))
        dsu.union((1, 2), (3, 4))
        self.assertTrue(dsu.same((1, 2), (3, 4)))

    def test_mixed_types(self):
        dsu = DisjointSetUnion()
        dsu.add(1)
        dsu.add("one")
        dsu.union(1, "one")
        self.assertTrue(dsu.same(1, "one"))
        self.assertEqual(dsu.size(1), 2)


class TestUnhashable(unittest.TestCase):
    def test_add_list_raises_typeerror(self):
        dsu = DisjointSetUnion()
        with self.assertRaises(TypeError):
            dsu.add([1, 2])

    def test_union_list_raises_typeerror(self):
        dsu = DisjointSetUnion()
        with self.assertRaises(TypeError):
            dsu.union([1], [2])

    def test_find_dict_raises_typeerror(self):
        dsu = DisjointSetUnion()
        with self.assertRaises(TypeError):
            dsu.find({1: 2})


class TestPathCompressionDeep(unittest.TestCase):
    def test_long_chain_all_connected(self):
        dsu = DisjointSetUnion()
        n = 50
        for i in range(n):
            dsu.add(i)
        for i in range(1, n):
            dsu.union(i - 1, i)
        root = dsu.find(0)
        for i in range(n):
            self.assertEqual(dsu.find(i), root)
        self.assertEqual(dsu.size(0), n)
        self.assertEqual(dsu.num_sets(), 1)

    def test_path_compression_flattens(self):
        """After find, every node on the path points directly at the root."""
        dsu = DisjointSetUnion()
        for i in range(5):
            dsu.add(i)
        # Build a chain 0 <- 1 <- 2 <- 3 <- 4 (via successive unions of small
        # sets; direction depends on union-by-size, so we check the invariant
        # indirectly: after find, re-finding is cheap and consistent).
        dsu.union(0, 1)
        dsu.union(1, 2)
        dsu.union(2, 3)
        dsu.union(3, 4)
        root = dsu.find(4)
        # After compression, the parent of 4 should be the root directly.
        self.assertEqual(dsu._parent[4], root)


class TestAlias(unittest.TestCase):
    def test_dsu_alias_same_class(self):
        self.assertIs(DSU, DisjointSetUnion)
        self.assertIs(CoreDSU, CoreDisjointSetUnion)
        self.assertIs(DSU, CoreDSU)

    def test_dsu_alias_works(self):
        dsu = DSU()
        dsu.union(1, 2)
        self.assertTrue(dsu.same(1, 2))


class TestEmptyStructures(unittest.TestCase):
    def test_empty_len(self):
        self.assertEqual(len(DisjointSetUnion()), 0)

    def test_empty_num_sets(self):
        self.assertEqual(DisjointSetUnion().num_sets(), 0)

    def test_empty_contains_nothing(self):
        self.assertNotIn(0, DisjointSetUnion())


if __name__ == "__main__":
    unittest.main()
