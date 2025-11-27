import can
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CAN_BUS")

class CanInterface:
    def __init__(self, channel='virtual_channel', interface='virtual'):
        """
        Initializes the CAN Bus interface.
        For Windows/Testing use interface='virtual'.
        For Linux/Production use interface='socketcan'.
        """
        self.channel = channel
        self.interface = interface
        self.bus = None

    def connect(self):
        try:
            self.bus = can.interface.Bus(channel=self.channel, interface=self.interface)
            logger.info(f"Connected to CAN Bus: {self.channel} ({self.interface})")
        except Exception as e:
            logger.error(f"Failed to connect to CAN Bus: {e}")
            raise e

    def send_message(self, arbitration_id, data_bytes):
        """
        Sends a raw CAN message.
        """
        if not self.bus:
            logger.warning("Bus not connected. Message dropped.")
            return

        message = can.Message(
            arbitration_id=arbitration_id,
            data=data_bytes,
            is_extended_id=False
        )

        try:
            self.bus.send(message)
            # Optional: Debug print for every message (can be noisy)
            # logger.debug(f"TX ID={hex(arbitration_id)} Data={data_bytes.hex()}")
        except can.CanError as e:
            logger.error(f"Message send failed: {e}")

    def shutdown(self):
        if self.bus:
            self.bus.shutdown()
            logger.info("CAN Bus shutdown.")