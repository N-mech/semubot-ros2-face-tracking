import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import serial

class HardwareNode(Node):
    def __init__(self):
        super().__init__('hardware_node')
        self.get_logger().info("Hardware Interface starting... 🔌")

        self.ser = None
        ports = ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyACM0', '/dev/ttyACM1']
        
        for p in ports:
            try:
                self.ser = serial.Serial(p, 115200, timeout=0.1)
                self.get_logger().info(f"✅ Connected to Arduino on {p}")
                break
            except Exception:
                pass

        if self.ser is None:
            self.get_logger().error("❌ Could not connect to Arduino! Check usbipd.")

        self.subscription = self.create_subscription(Twist, 'cmd_vel', self.cmd_callback, 10)

    def cmd_callback(self, msg):
        if self.ser:
            speed = msg.angular.z
            command = f"{speed:.3f}\n"
            try:
                self.ser.write(command.encode('utf-8'))
            except Exception as e:
                self.get_logger().error(f"Serial write failed: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = HardwareNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down Hardware Node... 🛑")
    finally:
        if node.ser:
            node.ser.close()
        node.destroy_node()
        rclpy.try_shutdown()

if __name__ == '__main__':
    main()