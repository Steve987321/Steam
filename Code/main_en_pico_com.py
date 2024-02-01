import time
from serial.tools import list_ports
import serial
# 25-1-2024


def read_serial(port):
    """Read data from serial port and return as string."""
    line = port.read(1000)
    return line.decode()


def pico_com():
    # Open a connection to the Pico
    with serial.Serial(port=pico_port, baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=1) as serial_port:
        serial_port_ = serial_port
        if serial_port.isOpen():
            print("[INFO] Using serial port", serial_port.name)
        else:
            print("[INFO] Opening serial port", serial_port.name, "...")
            serial_port.open()

        try:
            data = f"{lists}\r"
            print(data)
            serial_port.write(data.encode())
            pico_output = read_serial(serial_port)
            pico_output = pico_output.replace('\r\n', ' ')
            print(f"PICO output (test): {pico_output}")
            # Exit user input loop

        except KeyboardInterrupt:
            print("[INFO] Ctrl+C detected. Terminating.")

#------------------------------------------
lists = "[['echte', '*****'], ['*****'], ['*****']]"
serial_port_ = None

# First manually select the serial port that connects to the Pico
serial_ports = list_ports.comports()

print("[INFO] Serial ports found:")
for i, port in enumerate(serial_ports):
    print(str(i) + ". " + str(port.device))

#pico_port_index = int(input("Which port is the Raspberry Pi Pico connected to? "))
pico_port = serial_ports[0].device
pico_com()


    # # Close connection to Pico
    # serial_port.close()
    # print("[INFO] Serial port closed. Bye.")
