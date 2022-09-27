# co2 data logging plugin 
# when on, logs co2 information from sensor 

# scd-30 

from pioreactor.background_jobs.base import BackgroundJob
from pioreactor.actions.led_intensity import led_intensity
from pioreactor.config import config
from pioreactor.utils import timing
import board
import adafruit_scd30
import adafruit_scd4x

class CO2Reading(BackgroundJob):

    job_name="co2_reading"
    
    published_settings = {
        'minutes_between_checks': {'datatype': 'float', 'unit': 'min', 'settable': True},
        'co2': {'datatype': 'float', 'unit': 'ppm', 'settable': False}
    }
    
    def __init__(
        self, 
        unit, 
        experiment, 
        minutes_between_checks: float #config stuff, settable in activities 
    ):
        super().__init__(unit=unit, experiment=experiment)
        
        self.minutes_between_checks = minutes_between_checks
        self.on = start_on
        
        i2c = board.I2C()
       
        if config.getfloat("co2_config", "adafruit_sensor_type") == 'scd30':
            self.scd = adafruit_scd30.SCD30(i2c)
        elif config.getfloat("co2_config", "adafruit_sensor_type") == 'scd4x': 
            self.scd = adafruit_scd4x.SCD4X(i2c)
            self.scd.start_periodic_measurement()
        else:
            raise ValueError
       
        
        self.record_co2_timer = timing.RepeatedTimer(self.minutes_between_checks * 60, self.record_co2, run_immediately=True)
        
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
        
    
