#ifndef SENSORS_H
#define SENSORS_H

#include <Arduino.h>
#include <DHT.h>

inline float readSoilMoisture(int pin) {
    int raw = analogRead(pin);
    return 100.0f * (4095 - raw) / 4095.0f;
}

inline float readLight(int pin) {
    int raw = analogRead(pin);
    return map(raw, 0, 4095, 0, 60000);
}

inline float readTemperature(DHT &dht) { return dht.readTemperature(); }
inline float readHumidity(DHT &dht) { return dht.readHumidity(); }

#endif
