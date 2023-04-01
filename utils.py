def is_number(n):
    """Перевірка на числове значення"""
    try:
        float(n)
    except ValueError:
        return False
    return True
def connector_decorator(func):
    def wrapper(*args, **kwargs):
        def function():
            func(*args, **kwargs)
        return function
    return wrapper
