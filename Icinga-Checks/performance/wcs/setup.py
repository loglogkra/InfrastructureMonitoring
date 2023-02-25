#!/usr/local/bin/python3.6


from setuptools import setup

__version__ = "0.1"


setup(
    name="sysperf",
    version=__version__,
    packages=["sysperf"],
    description="Collection of system performance checks designed to be used by Icinga2.",
    install_requires=["cx_Oracle", "requests"]
    )

