#define STEP_PIN 2
#define DIR_PIN 3

long stepDelay = 0;
unsigned long lastStepTime = 0;

void setup() {
  Serial.begin(115200); // سرعة اتصال عالية لتقليل التأخير
  pinMode(STEP_PIN, OUTPUT);
  pinMode(DIR_PIN, OUTPUT);
  Serial.setTimeout(10);
}

void loop() {
  // 1. استقبال الأوامر من ROS 2
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    float target_speed = input.toFloat();

    if (target_speed == 0.0) {
      stepDelay = 0; // إيقاف المحرك
    } else {
      // تحديد الاتجاه
      if (target_speed > 0) {
        digitalWrite(DIR_PIN, HIGH);
      } else {
        digitalWrite(DIR_PIN, LOW);
      }

      // 2. التحويل من سرعة زاوية (rad/s) إلى نبضات
      // 400 نبضة للدرايفر * 27 نسبة الجيربوكس = 10800 نبضة للدورة
      float steps_per_sec = (abs(target_speed) / 6.28318) * 10800.0;

      if (steps_per_sec > 0) {
        stepDelay = 1000000 / steps_per_sec; 
      } else {
        stepDelay = 0;
      }
    }
  }

  // 3. توليد النبضات للمحرك
  if (stepDelay > 0) {
    if (micros() - lastStepTime >= stepDelay) {
      digitalWrite(STEP_PIN, HIGH);
      delayMicroseconds(2); 
      digitalWrite(STEP_PIN, LOW);
      lastStepTime = micros();
    }
  }
}