import unittest
import asyncio
from mixed_run import MixedRunner
import time
import timeit


class TestRunSync(unittest.TestCase):

    @classmethod
    def sync_fn(cls, x):
        return x * 2

    @classmethod
    async def async_fn(cls, x):
        await asyncio.sleep(0.01)
        return x * 3

    def test_sync_fn_in_sync_context(self):
        runner = MixedRunner()
        result = runner.run_sync(TestRunSync.sync_fn, 5)
        self.assertEqual(result, 10)

    def test_async_fn_in_sync_context(self):
        runner = MixedRunner()
        result = runner.run_sync(TestRunSync.async_fn, 5)
        self.assertFalse(asyncio.iscoroutine(result))
        self.assertEqual(result, 15)

    def test_sync_fn_in_async_context(self):
        async def test():
            runner = MixedRunner()
            return runner.run_sync(TestRunSync.sync_fn, 5)

        result = asyncio.run(test())
        self.assertEqual(result, 10)

    def test_async_fn_in_async_context(self):
        async def test():
            runner = MixedRunner()
            return runner.run_sync(TestRunSync.async_fn, 5)

        result = asyncio.run(test())
        self.assertEqual(result, 15)


class TestRunAsync(unittest.TestCase):
    core_waiting = 2

    @classmethod
    def sync_fn(cls, x, result_list):
        time.sleep(TestRunAsync.core_waiting)
        result_list.append(("sync", x * 2))

    @classmethod
    async def async_fn(cls, x, result_list):
        await asyncio.sleep(TestRunAsync.core_waiting)
        result_list.append(("async", x * 3))


    def test_sync_fn_in_sync_context(self):
        runner = MixedRunner()
        results = []
        t = timeit.timeit(lambda: runner.run_async(TestRunAsync.sync_fn, 5, results), number=1)
        self.assertLess(t, 0.5)
        time.sleep(TestRunAsync.core_waiting + 1)
        self.assertIn(("sync", 10), results)

    def test_async_fn_in_sync_context(self):
        runner = MixedRunner()
        results = []
        t = timeit.timeit(lambda: runner.run_async(TestRunAsync.async_fn, 5, results), number=1)
        self.assertLess(t, 0.5)
        time.sleep(TestRunAsync.core_waiting + 1)
        self.assertIn(("async", 15), results)

    def test_sync_fn_in_async_context(self):
        runner = MixedRunner()
        results = []

        async def test():
            t = timeit.timeit(lambda: runner.run_async(TestRunAsync.sync_fn, 5, results), number=1)
            self.assertLess(t, 0.5)
            await asyncio.sleep(TestRunAsync.core_waiting + 1)
            return results.copy()

        result = asyncio.run(test())
        self.assertIn(("sync", 10), result)

    def test_async_fn_in_async_context(self):
        runner = MixedRunner()
        results = []

        async def test():
            t = timeit.timeit(lambda: runner.run_async(TestRunAsync.async_fn, 5, results), number=1)
            self.assertLess(t, 0.5)
            await asyncio.sleep(TestRunAsync.core_waiting + 1)
            return results.copy()

        result = asyncio.run(test())
        self.assertIn(("async", 15), result)


if __name__ == "__main__":
    unittest.main()
