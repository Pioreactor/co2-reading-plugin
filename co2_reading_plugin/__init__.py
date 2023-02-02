# -*- coding: utf-8 -*-
from __future__ import annotations

import click
from pioreactor.background_jobs.base import BackgroundJob
from pioreactor.background_jobs.leader.mqtt_to_db_streaming import produce_metadata
from pioreactor.background_jobs.leader.mqtt_to_db_streaming import register_source_to_sink
from pioreactor.background_jobs.leader.mqtt_to_db_streaming import TopicToParserToTable
from pioreactor.config import config
from pioreactor.exc import HardwareNotFoundError
from pioreactor.hardware import SCL
from pioreactor.hardware import SDA
from pioreactor.utils import is_pio_job_running
from pioreactor.utils import timing
from pioreactor.whoami import get_latest_experiment_name
from pioreactor.whoami import get_unit_name
from pioreactor.whoami import is_testing_env


def parser(topic, payload) -> dict:
    metadata = produce_metadata(topic)
    return {
        "experiment": metadata.experiment,
        "pioreactor_unit": metadata.pioreactor_unit,
        "timestamp": timing.current_utc_timestamp(),
        "co2_reading_ppm": float(payload),
    }


register_source_to_sink(
    TopicToParserToTable(
        ["pioreactor/+/+/scd_reading/co2", "pioreactor/+/+/co2_reading/co2"],
        parser,
        "co2_readings",
    )
)


class SCDReading(BackgroundJob):

    job_name = "scd_reading"

    published_settings = {
        "interval": {"datatype": "float", "unit": "s", "settable": True},
        "co2": {"datatype": "float", "unit": "ppm", "settable": False},
        "temperature": {"datatype": "float", "unit": "°C", "settable": False},
        "relative_humidity": {"datatype": "float", "unit": "%rH", "settable": False},
    }

    def __init__(
        self,
        unit: str,
        experiment: str,
        interval: float,
        skip_co2: bool = False,
        skip_temperature: bool = False,
        skip_relative_humidity: bool = False,
    ) -> None:
        super().__init__(unit=unit, experiment=experiment)

        self.interval = interval
        self.skip_co2 = skip_co2
        self.skip_temperature = skip_temperature
        self.skip_relative_humidity = skip_relative_humidity

        if is_pio_job_running("co2_reading"):
            self.clean_up()
            raise ValueError("co2 reading can't be running at the same time")

        if not is_testing_env():
            from busio import I2C

            i2c = I2C(SCL, SDA)
        else:
            from pioreactor.utils.mock import MockI2C

            i2c = MockI2C(SCL, SDA)

        if config.get("scd_config", "adafruit_sensor_type") == "scd30":
            try:
                from adafruit_scd30 import SCD30

                self.scd = SCD30(i2c)
            except Exception:
                self.logger.error("Is the SCD30 board attached to the Pioreactor HAT?")
                raise HardwareNotFoundError("Is the SCD30 board attached to the Pioreactor HAT?")
        elif config.get("scd_config", "adafruit_sensor_type") == "scd4x":
            try:
                from adafruit_scd4x import SCD4X

                self.scd = SCD4X(i2c)
                self.scd.start_periodic_measurement()
            except Exception:
                self.logger.error("Is the SCD4X board attached to the Pioreactor HAT?")
                raise HardwareNotFoundError("Is the SCD4X board attached to the Pioreactor HAT?")
        else:
            self.logger.error(
                "'adafruit_sensor_type' in [scd_config] not found. Did you mean one of 'scd30' or 'scd4x'?"
            )
            raise ValueError(
                "'adafruit_sensor_type' in [scd_config] not found. Did you mean one of 'scd30' or 'scd4x'?"
            )

        self.record_scd_timer = timing.RepeatedTimer(
            self.interval, self.record_from_scd, run_immediately=True
        )

        self.record_scd_timer.start()

    def set_interval(self, new_interval) -> None:
        self.record_scd_timer.interval = new_interval
        self.interval = new_interval

    def on_sleeping(self) -> None:
        # user pauses
        self.record_scd_timer.pause()

    def on_sleeping_to_ready(self) -> None:
        self.record_scd_timer.unpause()

    def on_disconnect(self) -> None:
        self.record_scd_timer.cancel()

    def record_co2(self) -> None:
        self.co2 = self.scd.CO2

    def record_temperature(self) -> None:
        self.temperature = self.scd.temperature

    def record_relative_humidity(self) -> None:
        self.relative_humidity = self.scd.relative_humidity

    def record_from_scd(self) -> None:
        # determines which scd to record
        if not self.skip_co2:
            self.record_co2()
        if not self.skip_temperature:
            self.record_temperature()
        if not self.skip_relative_humidity:
            self.record_relative_humidity()


class CO2Reading(SCDReading):
    job_name = "co2_reading"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, skip_temperature=True, skip_relative_humidity=True, **kwargs)  # type: ignore
        if is_pio_job_running("scd_reading"):
            self.clean_up()
            raise ValueError("scd reading can't be running at the same time")


@click.command(name="scd_reading")
@click.option(
    "--interval",
    default=config.getfloat("scd_config", "interval"),
    show_default=True,
)
def click_scd_reading(interval) -> None:
    """
    Start reading CO2, temperature, and humidity from the scd sensor.
    """
    job = SCDReading(
        interval=interval,
        unit=get_unit_name(),
        experiment=get_latest_experiment_name(),
    )
    job.block_until_disconnected()


@click.command(name="co2_reading")
@click.option(
    "--interval",
    default=config.getfloat("scd_config", "interval"),
    show_default=True,
)
def click_co2_reading(interval) -> None:
    """
    Only returns CO2 readings.
    """
    job = CO2Reading(
        interval=interval,
        unit=get_unit_name(),
        experiment=get_latest_experiment_name(),
    )
    job.block_until_disconnected()
