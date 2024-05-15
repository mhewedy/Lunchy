import time
from typing import Callable, Any


def retry_function(func: Callable, retries: int = 5, delay: int = 1, *args, **kwargs) -> Any:
    attempts = 0
    while attempts < retries:
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            attempts += 1
            print(f"Attempt calling {func} #{attempts} failed with error: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)
    raise Exception(f"Function {func} failed after {retries} attempts")
