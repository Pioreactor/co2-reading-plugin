# -*- coding: utf-8 -*-
from __future__ import annotations

from setuptools import find_packages
from setuptools import setup


setup(
    name="co2_reading_plugin",
    version="0.1.3",
    license="MIT",
    description="Return a CO₂ reading every interval from an Adafruit CO₂ sensors SCD30, SCD40 or SCD41.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author_email="cam@pioreactor.com",
    author="Kelly Tran, Cameron Davidson-Pilon",
    url="https://github.com/Pioreactor/co2_reading_plugin",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["adafruit-circuitpython-scd30", "adafruit-circuitpython-scd4x"],
    entry_points={"pioreactor.plugins": "co2_reading_plugin = co2_reading_plugin"},
)
