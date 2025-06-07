#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <DHT.h>
#include <WebServer.h>
#include "FS.h"
#include "SPIFFS.h"
#include "esp_task_wdt.h"

// === CONFIG ===
#define SOIL_MOISTURE_AO_PIN 33
#define LIGHT_AO_PIN 35
#define TEMP_PIN 32
#define PUMP_PIN 4
#define DHTTYPE DHT11
const char* backend_url = "http://192.168.1.137:8000/api/sensor-data";
const char* wifi_log_url = "http://192.168.1.137:8000/api/wifi-log";

DHT dht(TEMP_PIN, DHTTYPE);
WebServer server(80);
String ssid, password;

// === INIT ===
void initSPIFFS() {
  if (!SPIFFS.begin(true)) {
    Serial.println("❌ SPIFFS mount failed");
  } else {
    Serial.println("✅ SPIFFS mounted");
  }
}

bool loadWiFiConfig() {
  File f = SPIFFS.open("/wifi.json", FILE_READ);
  if (!f || f.size() == 0) return false;
  StaticJsonDocument<128> doc;
  if (deserializeJson(doc, f)) return false;
  ssid = doc["ssid"].as<String>();
  password = doc["password"].as<String>();
  f.close();
  return true;
}

void saveWiFiConfig(const String& s, const String& p) {
  StaticJsonDocument<128> doc;
  doc["ssid"] = s;
  doc["password"] = p;
  File f = SPIFFS.open("/wifi.json", FILE_WRITE);
  serializeJson(doc, f);
  f.close();
}

// === AP ===
void handleRoot() {
  server.send(200, "text/html", R"rawliteral(
    <h2>Configurare WiFi SmartPlant</h2>
    <form method='POST' action='/set'>
      SSID:<br><input name='ssid'><br>
      Parola:<br><input name='pass' type='password'><br><br>
      <input type='submit' value='Salvează'>
    </form>
  )rawliteral");
}

void handleSet() {
  ssid = server.arg("ssid");
  password = server.arg("pass");

  Serial.println("📥 Cerere primită pe /set");
  Serial.printf("📶 SSID: %s\n", ssid.c_str());
  Serial.printf("🔐 PASS: %s\n", password.c_str());

  saveWiFiConfig(ssid, password);
  server.send(200, "text/html", "Salvat. Se restartează...");
  delay(2000);
  ESP.restart();
}

void handleResetWiFi() {
  SPIFFS.remove("/wifi.json");
  server.send(200, "text/plain", "WiFi config șters. Se restartează...");
  delay(1000);
  ESP.restart();
}

void startAPMode() {
  WiFi.softAP("SmartPlant_Setup");
  Serial.println("⚠️ WiFi fallback - pornit AP");
  Serial.println("🌐 Conectează-te la: SmartPlant_Setup");

  server.on("/", handleRoot);
  server.on("/set", HTTP_POST, handleSet);
  server.on("/reset-wifi", HTTP_POST, handleResetWiFi);
  server.begin();
}

// === NET STATUS ===
void logWiFiStatus() {
  if (WiFi.status() != WL_CONNECTED) return;

  StaticJsonDocument<128> doc;
  doc["ssid"] = ssid;
  doc["ip_address"] = WiFi.localIP().toString();
  doc["status"] = "online";

  String payload;
  serializeJson(doc, payload);

  HTTPClient http;
  http.begin(wifi_log_url);
  http.addHeader("Content-Type", "application/json");
  int code = http.POST(payload);
  http.end();

  Serial.print("📤 WiFi log trimis: ");
  Serial.println(code == 200 ? "✅ OK" : "❌ Eroare");
}

void tryConnectWiFi() {
  if (!loadWiFiConfig()) {
    Serial.println("❌ Nu există config WiFi");
    startAPMode();
    return;
  }

  WiFi.begin(ssid.c_str(), password.c_str());
  Serial.printf("🔌 Conectare la %s...\n", ssid.c_str());

  unsigned long t0 = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - t0 < 10000) {
    Serial.print(".");
    delay(500);
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✅ Conectat!");
    Serial.print("IP: "); Serial.println(WiFi.localIP());
    logWiFiStatus();
  } else {
    Serial.println("\n❌ Conexiune eșuată");
    startAPMode();
  }
}

// === BUFFER ===
void saveToBuffer(const String& payload) {
  File file = SPIFFS.open("/buffer.json", FILE_APPEND);
  if (file) {
    file.println(payload);
    file.close();
    Serial.println("💾 Salvat în buffer SPIFFS");
  }
}

bool sendToServer(const String& payload) {
  if (WiFi.status() != WL_CONNECTED) return false;
  HTTPClient http;
  http.begin(backend_url);
  http.addHeader("Content-Type", "application/json");
  int code = http.POST(payload);
  http.end();
  Serial.printf("🌐 POST status: %d\n", code);
  return code == 200;
}

void flushBufferToServer() {
  File file = SPIFFS.open("/buffer.json", FILE_READ);
  if (!file || file.size() == 0) return;

  Serial.println("🚚 Retrimit date din buffer...");
  while (file.available()) {
    String line = file.readStringUntil('\n');
    if (!sendToServer(line)) {
      Serial.println("❌ Eroare. Buffer păstrat.");
      file.close();
      return;
    }
    delay(500);
  }

  file.close();
  SPIFFS.remove("/buffer.json");
  Serial.println("✅ Buffer golit complet");
}

// === SENSORS ===
String collectSensorJSON() {
  int soil_raw = analogRead(SOIL_MOISTURE_AO_PIN);
  float soil_percent = 100.0 * (4095 - soil_raw) / 4095.0;
  int light_raw = analogRead(LIGHT_AO_PIN);
  float light_value = map(light_raw, 0, 4095, 0, 60000);
  float temp = dht.readTemperature();
  float humidity = dht.readHumidity();

  StaticJsonDocument<256> doc;
  doc["plant_type"] = "rosie";
  doc["soil_moisture"] = soil_percent;
  doc["temperature"] = temp;
  doc["air_humidity"] = humidity;
  doc["light"] = light_value;

  String payload;
  serializeJson(doc, payload);
  Serial.printf("🌱 %.1f%% | ☀️ %.0f | 🌡️ %.1f°C | 💧 %.1f%%\n", soil_percent, light_value, temp, humidity);
  return payload;
}

// === MAIN ===
void setup() {
  Serial.begin(115200);
  pinMode(PUMP_PIN, OUTPUT);
  digitalWrite(PUMP_PIN, LOW);
  dht.begin();
  initSPIFFS();
  tryConnectWiFi();
  esp_task_wdt_init(10, true);
  esp_task_wdt_add(NULL);
}

void loop() {
  esp_task_wdt_reset();

  if (WiFi.getMode() == WIFI_AP) {
    server.handleClient();
    delay(10);
    return;
  }

  String payload = collectSensorJSON();

  if (WiFi.status() == WL_CONNECTED) {
    if (sendToServer(payload)) {
      Serial.println("✅ Date trimise");
      flushBufferToServer();
    } else {
      Serial.println("📥 Trimitere eșuată. Salvăm.");
      saveToBuffer(payload);
    }
  } else {
    Serial.println("❌ Fără WiFi – salvăm local");
    saveToBuffer(payload);
  }

  delay(60000); // 1 minut
}
