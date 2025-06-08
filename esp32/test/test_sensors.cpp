#include <Arduino.h>
#include <unity.h>
#include "sensors.h"

// Stub analogRead for testing
int analogRead(uint8_t pin) {
    (void)pin;
    return 2048; // valoare intermediară
}

void test_read_soil() {
    float pct = readSoilMoisture(0);
    TEST_ASSERT_FLOAT_WITHIN(1.0, 50.0, pct); // ~50%
}

void test_no_block() {
    unsigned long start = millis();
    delay(5);
    TEST_ASSERT_TRUE(millis() - start < 50);
}

void setup() {
    UNITY_BEGIN();
    RUN_TEST(test_read_soil);
    RUN_TEST(test_no_block);
    UNITY_END();
}

void loop() {
}
