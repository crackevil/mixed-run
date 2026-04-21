import asyncio

import janus
import threading
import functools
import nest_asyncio

nest_asyncio.apply()

def AsyncioRunningLoop():
    try:
       return asyncio.get_running_loop()
    except RuntimeError:
       pass


class MixedRunner(object):

    def __init__(self):
        self.AsyncRunnerThread = None
        self.__MQ__ = None
        self.thread_ready = threading.Event()

    def run_sync(self, fn, *args, **kwargs):
        result = fn(*args, **kwargs)
        if asyncio.iscoroutine(result):
            loop = AsyncioRunningLoop()
            result = loop.run_until_complete(result) if loop else asyncio.run(result)  #run_until_complete works since nest_asyncio

        return result

    def run_async(self, fn, *args, **kwargs):

        async def async_wrapper(fn, *args, **kwargs):
            return fn(*args, **kwargs)

        def __thread_target__():

            async def __target__():
                if not self.__MQ__:
                    self.__MQ__ = janus.Queue()
                    self.thread_ready.set()
                while True:
                    func = await self.__MQ__.async_q.get()
                    self.run_async(func)
                # close the queue, although it never reach here by the infinite while
                self.thread_ready.clear()
                await self.__MQ__.aclose()
                self.__MQ__ = None

            asyncio.run(__target__())

        loop = AsyncioRunningLoop()
        if loop:
            # return awaitable in async context, could be await when need
            if asyncio.iscoroutinefunction(fn):
                return asyncio.create_task(fn(*args, **kwargs))
            elif asyncio.iscoroutine(fn):
                return asyncio.create_task(fn)
            else:
                return asyncio.create_task(async_wrapper(fn, *args, **kwargs))
        else:
            if not self.AsyncRunnerThread:
                self.AsyncRunnerThread = threading.Thread(target=__thread_target__, daemon=True)
                self.AsyncRunnerThread.start()
            wrapped = functools.partial(fn, *args, **kwargs)
            if not asyncio.iscoroutinefunction(fn):
                wrapped = async_wrapper(wrapped)
            self.thread_ready.wait()
            self.__MQ__.sync_q.put(wrapped)

