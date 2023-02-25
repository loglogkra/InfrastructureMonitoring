#!/usr/local/bin/python3.6

import psutil


def Mem_Free():
    """Course granularity Memory OK check.
        Returns a single value representing the free memory that is available.
    """
    mem = 100 - psutil.virtual_memory().percent

    #print(str(mem))

    return mem

if __name__ == '__main__':
    retval = Mem_Free()
    print(retval)

