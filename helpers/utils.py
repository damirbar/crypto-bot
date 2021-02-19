import threading


def set_interval(interval=60):  # interval in seconds
    def decorator(func):
        def wrap(*args, **kwargs):
            stop = threading.Event()

            def run():
                while not stop.is_set():
                    stop.wait(interval)
                    func(*args, **kwargs)

            t = threading.Timer(0, run)
            t.daemon = True  # stop the thread when we finish execution
            t.start()
            return stop

        return wrap

    return decorator
