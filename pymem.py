import gc


def optimise_mem():
    print("LOG:      (pymem.py) - Python Garbage Collection Optimised")
    gc.collect(2)
    gc.freeze()

    allocs, gen1, gen2 = gc.get_threshold()
    allocs = 50_000
    gen1 = gen1 * 2
    gen2 = gen2 * 2
    gc.set_threshold(allocs, gen1, gen2)
