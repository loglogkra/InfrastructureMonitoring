import psutil


def Mem_Free(memThreash):
    """ Coarse granularity Memory OK check.
        Returns a single value representing the free memory that is available.
    """

    if memThreash is None:
        return []

    mem = 100 - psutil.virtual_memory().percent

    #print(str(mem))

    if mem < memThreash:
        return [mem]

    return []


if __name__ == '__main__':
    ret = Mem_Free(int(99))

    for elem in ret:
        print (elem)
