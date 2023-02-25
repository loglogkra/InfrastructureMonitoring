#!/usr/local/bin/python3.6

import psutil


def Cpu_Usage():
    """Course granularity CPU OK check.
        Samples the CPU utilization accross all logical processors and
        returns the average.
    """
    x = psutil.cpu_percent(interval=.2, percpu=True)
    cpu = sum(x)/len(x)

    return cpu

if __name__ == '__main__':
    Cpu_Usage()
