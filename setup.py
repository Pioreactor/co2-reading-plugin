# -*- coding: utf-8 -*-
from __future__ import annotations

from setuptools import find_packages
from setuptools import setup


setup(
    name="co2_reading_plugin",
    version="0.0.2",
    license="MIT",
    description="Return a CO2 reading every set minutes from Adafruit CO2 sensors SCD30, SCD40 or SCD41.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author_email="kelly@pioreactor.com",
    author="Kelly Tran",
    url="https://github.com/Pioreactor/co2_reading_plugin",
    packages=find_packages(),
    include_package_data=True,
    entry_points={"pioreactor.plugins": "co2_reading_plugin = co2_reading_plugin"},
)
