# -*- coding: utf-8 -*-
from __future__ import annotations

import adafruit_scd30
import adafruit_scd4x
import board
from pioreactor.background_jobs.base import BackgroundJob
from pioreactor.config import config
from pioreactor.utils import timing
from pioreactor.whoami import get_latest_testing_experiment_name
from pioreactor.whoami import get_unit_name


class SCDReading(BackgroundJob):

    job_name = "scd_reading"

    published_settings = {
        "minutes_between_checks": {"datatype": "float", "unit": "min", "settable": True},
        "co2": {"datatype": "float", "unit": "ppm", "settable": False},
        "temperature": {"datatype": "float", "unit": "degrees Celcius", "settable": False},
        "humidity": {"datatype": "float", "unit": "%rH", "settable": False},
    }

    def __init__(
        self,
        unit,
        experiment,
        minutes_between_checks: float,  # config stuff, settable in activities
    ):
        super().__init__(unit=unit, experiment=experiment)

        self.minutes_between_checks = minutes_between_checks
        self.on = True

        i2c = board.I2C()

        if config.getfloat("scd_config", "adafruit_sensor_type") == "scd30":
            self.scd = adafruit_scd30.SCD30(i2c)
        elif config.getfloat("scd_config", "adafruit_sensor_type") == "scd4x":
            self.scd = adafruit_scd4x.SCD4X(i2c)
            self.scd.start_periodic_measurement()
        else:
            raise ValueError

        self.record_timer = timing.RepeatedTimer(
            self.minutes_between_checks * 60, self.record_co2, run_immediately=True
        )
        # to be changed to record all?
        ###

        self.record_co2_timer.start()

    def set_minutes_between_checks(self, new_minutes_between_checks):
        self.record_co2_timer.interval = new_minutes_between_checks * 60
        self.minutes_between_checks = new_minutes_between_checks

    def on_sleeping(self):
        # user pauses
        self.record_co2_timer.pause()

    def on_sleeping_to_ready(self):
        self.record_co2_timer.unpause()

    def on_disconnect(self):
        self.record_co2_timer.cancel()

    def record_co2(self):
        co2_reading = self.scd.CO2

        self.co2 = co2_reading

    def record_temperature(self):
        temperature_reading = self.scd.temperature
        # retrieve temp reading from the scd sensor

        self.temperature = temperature_reading
        # assign class temperature as reading from scd sensor

    def record_humidity(self):
        humidity_reading = self.scd.relative_humidity

        self.temperature = humidity_reading


import click


@click.command(name="scd_reading")
@click.option(
    "--minutes_between_checks",
    default=config.getfloat("scd_config", "minutes_between_checks"),
    show_default=True,
    type=click.FloatRange(1, 10_000, clamp=True),
)
@click.option("--start-off", is_flag=True)
def click_scd_reading(minutes_between_checks, start_off):
    """
    Start reading CO2, temperature, and humidity from the scd sensor.
    """
    job = SCDReading(
        minutes_between_checks=minutes_between_checks,
        unit=get_unit_name(),
        experiment=get_latest_testing_experiment_name(),
        start_on=not start_off,
    )
    job.block_until_disconnected()


if __name__ == "__main__":
    click_scd_reading()
