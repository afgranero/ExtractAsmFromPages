import functools


def with_condition(condition):
    def decorator(func):
        func.condition = condition
        return func
    return decorator


def call_count(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.calls_count += 1
        return func(*args, **kwargs)

    wrapper.calls_count = 0
    return wrapper