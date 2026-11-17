import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
import cv2

class VisionNode(Node):
    def __init__(self):
        super().__init__('vision_node')
        self.get_logger().info("Vision Node starting... Face Tracking Active 👁️")
        
        # الناشر الذي سيرسل قيمة الخطأ الرياضي لباقي أجزاء الروبوت
        self.error_publisher = self.create_publisher(Float32, 'vision_error', 10)
        
        # فتح الكاميرا (0 هو الفهرس الافتراضي)
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.get_logger().error("⚠️ Camera not found! Check device permissions.")
            
        # المسار الافتراضي لملفات الذكاء الاصطناعي في نظام Ubuntu
        cascade_path = '/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        
        # التحقق من نجاح تحميل خوارزمية الوجه
        if self.face_cascade.empty():
            self.get_logger().error("⚠️ Failed to load face cascade! Check file path.")
        
        # مؤقت لتحديث الكاميرا 10 مرات في الثانية (10Hz)
        self.timer = self.create_timer(0.1, self.timer_callback)

    def timer_callback(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        # تحويل الصورة للأبيض والأسود لتسريع أداء خوارزمية الذكاء الاصطناعي
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # استخراج أبعاد الشاشة وتحديد خط المنتصف
        height, width, _ = frame.shape
        frame_center_x = width // 2
        
        # رسم خط أخضر عمودي في منتصف الشاشة كمرجع دائم (Setpoint)
        cv2.line(frame, (frame_center_x, 0), (frame_center_x, height), (0, 255, 0), 2)

        # البحث عن الوجوه في الصورة
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

        if len(faces) > 0:
            # نأخذ أول وجه تم اكتشافه (في حال وجود أكثر من شخص في الكادر)
            (x, y, w, h) = faces[0]
            
            # رسم مربع أزرق حول الوجه
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
            # حساب نقطة منتصف الوجه ورسم دائرة حمراء عليها
            face_center_x = x + (w // 2)
            cv2.circle(frame, (face_center_x, y + (h//2)), 5, (0, 0, 255), -1)
            
            # حساب الخطأ (المسافة بالبكسل بين الوجه ومنتصف الكاميرا)
            error = float(face_center_x - frame_center_x)
            
            # نشر قيمة الخطأ في شبكة ROS 2
            msg = Float32()
            msg.data = error
            self.error_publisher.publish(msg)
            
            # طباعة قيمة الخطأ على الشاشة لكي تراها بعينك
            cv2.putText(frame, f"Error: {error}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        else:
            # إذا لم يجد وجهاً، نرسل صفر لكي تتوقف الرقبة مكانها بأمان
            msg = Float32()
            msg.data = 0.0
            self.error_publisher.publish(msg)
            cv2.putText(frame, "No Face - Stop (Error: 0.0)", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # عرض النافذة وتحديثها
        cv2.imshow("SemuBot Vision", frame)
        cv2.waitKey(1) 

def main(args=None):
    rclpy.init(args=args)
    node = VisionNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down safely... 🛑")
    finally:
        # إغلاق الكاميرا والنوافذ بشكل آمن
        if node.cap.isOpened():
            node.cap.release()
        cv2.destroyAllWindows()
        node.destroy_node()
        rclpy.try_shutdown()

if __name__ == '__main__':
    main()