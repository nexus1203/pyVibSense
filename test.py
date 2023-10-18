import asyncio
import struct

DATA_PORT = 5255
HEADER = b"DATA_START"
FOOTER = b"DATA_END"
SAMPLES = 375  # Adjust this to your actual SAMPLES value
expected_size = SAMPLES * 3 * 4  # 3 floats for each SAMPLE, 4 bytes per float


class UDPServer:

    def __init__(self):
        self.buffer = bytearray()

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        # If HEADER is detected, reset the buffer
        if data == HEADER:
            self.buffer = bytearray()
            return

        # If FOOTER is detected, process the buffer
        if data == FOOTER:
            print(f"FOOTER received. Buffer size: {len(self.buffer)} bytes.")
            self.process_data()
            return

        # If neither HEADER nor FOOTER, then it's data
        self.buffer.extend(data)

    def process_data(self):
        # Ensure data has the expected size
        if len(self.buffer) != expected_size:
            print(
                f"Unexpected data size. Expected {expected_size} bytes, but received {len(self.buffer)} bytes."
            )
            return
        assert len(
            self.buffer
        ) == expected_size, f"Buffer size mismatch: {len(self.buffer)} vs {expected_size}"
        format_string = f'{3*SAMPLES}f'

        acc_data_list = struct.unpack(format_string, self.buffer)
        for i in range(0, len(acc_data_list), 3):
            x, y, z = acc_data_list[i:i + 3]
            # print(f"X: {x}, Y: {y}, Z: {z}")

        # Clear buffer after processing
        self.buffer = bytearray()


async def main():
    loop = asyncio.get_running_loop()
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: UDPServer(), local_addr=('0.0.0.0', DATA_PORT))
    try:
        await asyncio.sleep(3600)  # Run for 1 hour. You can adjust this.
    finally:
        transport.close()


asyncio.run(main())
