#!/usr/local/bin/python3.6

import psutil


def Cpu_Usage(cpuThreash):
    """ Coarse granularity CPU OK check.
        Samples the CPU utilization accross all logical processors and
        returns the average.
    """
    if cpuThreash is None:
        return []

    x = psutil.cpu_percent(interval=.2, percpu=True)
    cpu = sum(x)/len(x)

    if cpu > cpuThreash:
        return [cpu]

    return []


if __name__ == '__main__':
    ret = Cpu_Usage(int(1))

    for elem in ret:
        print (elem)
