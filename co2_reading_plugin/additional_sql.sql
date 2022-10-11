CREATE TABLE IF NOT EXISTS co2_readings (
    experiment               TEXT NOT NULL,
    pioreactor_unit          TEXT NOT NULL,
    timestamp                TEXT NOT NULL,
    co2_reading_ppm          REAL
);
