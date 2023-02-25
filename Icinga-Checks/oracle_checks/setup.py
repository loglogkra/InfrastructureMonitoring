#!/usr/local/bin/python3.6


from setuptools import setup

__version__ = "0.1"


setup(
    name="oracle_checks",
    version=__version__,
    packages=["oracle_checks"],
    description="Collection of system health checks designed to be used by Icinga2.",
    install_requires=["cx_Oracle"]
    )

