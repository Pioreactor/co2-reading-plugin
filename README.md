## Pioreactor CO2 reading plugin

Adafruit offers three CO2 sensors ([SCD30](https://www.adafruit.com/product/4867), [SCD40 and SCD41](https://learn.adafruit.com/adafruit-scd-40-and-scd-41)) that measure CO2, temperature, and humidity.

This is a simple Pioreactor plugin that returns CO2 readings (or all readings) at a set duration from stemma QT connected Adafruit SCD sensors.

Install with `pio plugins install co2-reading-plugin` from the command line, or in the Pioreactor UI.

> [!IMPORTANT]
> After installation, you'll need to edit your configuration to add the model of sensor you have. Find the section `[co2_reading.config]`, and edit parameter `adafruit_sensor_type` to be either `scd30` or  `scd4x`. (The `scd4x` represents both scd41 and scd40 sensors.q)


### Overview chart

This also adds a chart to your overview page that displays the CO2 readings per Pioreactor.
