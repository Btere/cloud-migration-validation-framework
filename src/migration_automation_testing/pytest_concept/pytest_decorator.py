import logging
from functools import wraps

logging.basicConfig(level=logging.INFO)

def log_test(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logging.info(f"Starting test: {func.__name__}")
        func(*args, **kwargs)
        logging.info(f"Finished test: {func.__name__}")
        return wrapper
    
###Why *args and **kwargs?

#They allow the decorator to work with functions containing different arguments.

