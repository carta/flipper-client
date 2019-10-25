import unittest

from flipper.contrib.util.iter import batchify


class TestBatchify(unittest.TestCase):
    def test_it_breaks_an_iterable_into_chunks(self):
        iterable = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        chunks = list(batchify(iterable, 2))

        self.assertEqual(5, len(chunks))

    def test_it_breaks_an_iterator_into_chunks(self):
        iterable = (x for x in range(10))

        chunks = list(batchify(iterable, 2))

        self.assertEqual(5, len(chunks))

    def test_when_list_does_not_divide_evenly_you_get_one_extra_chunk(self):
        iterable = range(11)

        chunks = list(batchify(iterable, 2))

        self.assertEqual(6, len(chunks))

    def test_chunks_contain_correct_items(self):
        iterable = range(11)

        chunks = list(batchify(iterable, 2))

        self.assertEqual([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9], [10]], chunks)

    def test_when_chunk_size_is_larger_than_iterable_size_returns_one_chunk(self):
        iterable = range(10)

        chunks = list(batchify(iterable, 20))

        self.assertEqual(1, len(chunks))
