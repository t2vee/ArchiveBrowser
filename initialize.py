import gc
import os
import sentry_sdk


def start_sentry_sdk():
    if os.environ.get("PRODUCTION"):
        traces_sample_rate = 0.5
    else:
        traces_sample_rate = 1.0
    sentry_sdk.init(
        dsn=f"{os.environ.get('SENTRY_DSN')}",
        traces_sample_rate=traces_sample_rate,
    )
    print("LOG:      (initialize.py) - Sentry SDK Started")


def optimise_mem():
    print("LOG:      (initialize.py) - Python Garbage Collection Optimised")
    gc.collect(2)
    gc.freeze()

    allocs, gen1, gen2 = gc.get_threshold()
    allocs = 50_000
    gen1 = gen1 * 2
    gen2 = gen2 * 2
    gc.set_threshold(allocs, gen1, gen2)
