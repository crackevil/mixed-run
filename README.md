# MixedRunner

`MixedRunner` is a utility class provides a unified semantical interface for calling function both syncly and asyncly. It works for calling sync and async functions from sync and async context without needing to know them in advance.

The implementation try best to reduce resource usage. It uses coroutines as much as possible, with a single thread for async ability when required.

## Interfaces

### `run_sync(fn, *args, **kwargs)`

Call a function syncly.
returns the result.

### `run_async(fn, *args, **kwargs)`

Call a function asyncly. Since the execution does not wait for the result, the called function `fn` need put the result to somewhere. It means `fn` will be considered as a 'procedure'.

returns an awaitable when inside an async context. It can be await at any time needed

## Usage Examples

### Using `run_sync`

```python

def sync_add(a, b):
    return a + b

runner = MixedRunner()
result = runner.run_sync(sync_add, 1, 2)
print(result)

async def async_multiply(a, b):
    return a * b

result = runner.run_sync(async_multiply, 3, 4)
print(result)
```

### Using `run_async`

```python


def sync_fn(cls, x, result_list):
    result_list.append(("sync", x * 2))

async def async_fn(cls, x, result_list):
    result_list.append(("async", x * 3))

runner = MixedRunner()
results1 = []
runner.run_async(sync_fn, 5, results1)
print(results1)

results2 = []
runner.run_async(TestRunAsync.async_fn, 5, results2)
print(results2)

```


