import struct
import bluepy.btle as btle
import sys
from time import sleep

heartrate_uuid = btle.UUID(0x2a37)

class heartMonitor:
    def __init__(self, mac):
        try:
            self.p = btle.Peripheral(mac)
            self.p.setDelegate(heartDelegate())
        except Exception as e:
            print(str(e))
            self.p = 0
            print("Not connected")

    def startMonitor(self):
        try:
            self.p.writeCharacteristic(0x12, struct.pack('<bb', 0x01, 0x00), False)
            self.p.writeCharacteristic(0x11, '\x04', False)
        except:
            e = sys.exc_info()[0]
            print("HeartMonitor Error: %s" % e)
            try:
                self.p.disconnect()
            except:
                return 0

    def getHeartbeat(self):
        try:
            self.p.waitForNotifications(1.0)
            return self.p.delegate.getlastbeat()
        except:
            return 0

    def stopMonitor(self):
        self.p.writeCharacteristic(0x11, '\x00', False)


class heartDelegate(btle.DefaultDelegate):
    message = 0

    def __init__(self):
        btle.DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        print(data)
        if(data[0] == '\x14'):
            self.message = "Connection Lost"
        if(data[0] == '\x16'):
            self.message = str(struct.unpack("B", data[1])[0])
        if(data[0] == '\x06'):
            self.message = "Booting"

    def getlastbeat(self):
        return self.message

import pygatt

# The BGAPI backend will attempt to auto-discover the serial device name of the
# attached BGAPI-compatible USB adapter.
adapter = pygatt.GATTToolBackend()

try:
    adapter.start()
    device = adapter.connect('F9:04:31:D8:94:B2')
    value = device.char_read("a1e8f5b1-696b-4e4c-87c6-69dfe0b0093b")
finally:
    adapter.stop()