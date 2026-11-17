import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from geometry_msgs.msg import Twist
import time

class PIDNode(Node):
    def __init__(self):
        super().__init__('pid_node')
        self.get_logger().info("PID Controller Node starting... Brain is online 🧠")

        # 1. مشترك (Subscriber): يستمع لرسائل "الخطأ" القادمة من عقدة الكاميرا
        self.subscription = self.create_subscription(
            Float32,
            'vision_error',
            self.error_callback,
            10)

        # 2. ناشر (Publisher): يرسل أوامر السرعة النهائية للمحرك (Twist)
        self.cmd_publisher = self.create_publisher(Twist, 'cmd_vel', 10)

        # 3. معاملات الـ PID (سنقوم بضبطها لاحقاً لتنعيم الحركة)
        self.kp = 0.005  # التناسبي (Proportional) - يحدد قوة التفاعل مع الخطأ
        self.ki = 0.000  # التكاملي (Integral)
        self.kd = 0.001  # التفاضلي (Derivative) - يمنع الاهتزاز عند التوقف

        self.prev_error = 0.0
        self.integral = 0.0
        self.prev_time = time.time()

    def error_callback(self, msg):
        current_error = msg.data
        current_time = time.time()
        dt = current_time - self.prev_time

        # إذا كان الخطأ صفراً (لم يتم اكتشاف وجه أو الوجه في المنتصف تماماً)
        if current_error == 0.0:
            self.stop_motor()
            self.prev_error = 0.0
            self.integral = 0.0
            self.prev_time = current_time
            return

        # حسابات الـ PID الرياضية
        if dt > 0:
            p_term = self.kp * current_error
            self.integral += current_error * dt
            i_term = self.ki * self.integral
            d_term = self.kd * (current_error - self.prev_error) / dt

            # السرعة المطلوبة للمحرك
            output_speed = p_term + i_term + d_term

            # حماية هندسية (Clipping): وضع حد أقصى للسرعة لحماية الميكانيكا
            max_speed = 2.0
            if output_speed > max_speed: output_speed = max_speed
            elif output_speed < -max_speed: output_speed = -max_speed

            self.publish_speed(output_speed)

        self.prev_error = current_error
        self.prev_time = current_time

    def publish_speed(self, speed):
        twist_msg = Twist()
        # نضع السرعة في محور الزاوية Z (لأن الرقبة تدور أفقياً Pan)
        # الإشارة السالبة قد نحتاجها لعكس الاتجاه حسب الكاميرا
        twist_msg.angular.z = float(-speed) 
        self.cmd_publisher.publish(twist_msg)
        self.get_logger().info(f"Target Acquired! Sending Motor Speed: {twist_msg.angular.z:.3f} rad/s")

    def stop_motor(self):
        twist_msg = Twist()
        twist_msg.angular.z = 0.0
        self.cmd_publisher.publish(twist_msg)
        self.get_logger().info("Centered or No Face. Motor Stopped (Speed: 0.0)")

def main(args=None):
    rclpy.init(args=args)
    node = PIDNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down PID Node... 🛑")
    finally:
        node.destroy_node()
        rclpy.try_shutdown()

if __name__ == '__main__':
    main()