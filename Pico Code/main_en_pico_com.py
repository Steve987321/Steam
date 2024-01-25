import time
from serial.tools import list_ports
import serial


def read_serial(port):
    """Read data from serial port and return as string."""
    line = port.read(1000)
    return line.decode()


# First manually select the serial port that connects to the Pico
serial_ports = list_ports.comports()

print("[INFO] Serial ports found:")
for i, port in enumerate(serial_ports):
    print(str(i) + ". " + str(port.device))

pico_port_index = int(input("Which port is the Raspberry Pi Pico connected to? "))
pico_port = serial_ports[pico_port_index].device

lists = "[['Damian'], ['Duncan'], ['Damian;GAME']]"  # -------------------------------------------------------------
while True:
    close_or_not = input("Continue or close? ")
    if close_or_not == "close":
        break

    # Open a connection to the Pico
    with serial.Serial(port=pico_port, baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=1) as serial_port:
        if serial_port.isOpen():
            print("[INFO] Using serial port", serial_port.name)
        else:
            print("[INFO] Opening serial port", serial_port.name, "...")
            serial_port.open()

        try:
            data = f"{lists}\r"
            serial_port.write(data.encode())
            pico_output = read_serial(serial_port)
            pico_output = pico_output.replace('\r\n', ' ')
            # Exit user input loop

        except KeyboardInterrupt:
            print("[INFO] Ctrl+C detected. Terminating.")
    time.sleep(10)

# Close connection to Pico
serial_port.close()
print("[INFO] Serial port closed. Bye.")
