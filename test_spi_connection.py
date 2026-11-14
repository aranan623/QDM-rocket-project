from LoRaRF import SX127x

LoRa = SX127x()

print("Trying to talk to the Ra-02 over SPI...")

if LoRa.begin():
    print("SUCCESS: Ra-02 detected and responding correctly.")
else:
    print("FAILED: Could not detect the Ra-02.")
    print("Check wiring against the wiring table, that SPI is enabled,")
    print("that GND is connected, and that power is 3.3V not 5V.")

LoRa.end()
