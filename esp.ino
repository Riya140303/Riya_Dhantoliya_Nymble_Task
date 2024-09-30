#include <EEPROM.h>

#define EEPROM_ADDRESS 0

void setup() {
    Serial.begin(2400);
}

void loop() {
    if (Serial.available()) {
        String data = Serial.readStringUntil('\n');
        
        for (int i = 0; i < data.length() && i < 117; i++) {
            EEPROM.write(EEPROM_ADDRESS + i, data[i]);
        }
        EEPROM.write(EEPROM_ADDRESS + data.length(), '\0');
        
        Serial.println("Data stored in EEPROM.");

        if (data == "READ") {
            String readData;
            for (int i = 0; i < 117; i++) {
                char c = EEPROM.read(EEPROM_ADDRESS + i);
                if (c == '\0') break;
                readData += c;
                delay(2);
            }
            Serial.println(readData);
        }
    }
}
