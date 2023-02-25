#!/usr/local/bin/python3.6


from setuptools import setup

__version__ = "0.1"


setup(
    name="syshealth",
    version=__version__,
    packages=["syshealth"],
    description="Collection of system health checks designed to be used by Icinga2.",
    install_requires=["cx_Oracle", "psutil"]
    )

