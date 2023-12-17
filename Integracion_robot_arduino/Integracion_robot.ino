#include <Wire.h>
#include "compass.h"
#include <ros.h>
#include <std_msgs/Float32.h>
#include <std_msgs/Int8.h>
#include <std_msgs/Int16.h>
#include <std_msgs/Empty.h>

// Pines
const uint8_t optic_sensor = 2;
const uint8_t PwmMotorRight = 5;
const uint8_t in1Right = 7;
const uint8_t in2Right = 6;
const uint8_t in1Left = 9;
const uint8_t in2Left = 8;
const uint8_t PwmMotorLeft = 10;
const uint8_t yellow_button = 13;
const uint8_t in1motor_pasos = 3;
const uint8_t in2motor_pasos = 4;
const uint8_t in3motor_pasos = 11;
const uint8_t in4motor_pasos = 12;
int retardo = 3;
int cont_horario = 0;
int cont_antihorario = 0;
int pos_global_motorpasos = 0;
bool motorpasos_active = false;
ros::NodeHandle  nh;
std_msgs::Float32 imu_msg;
std_msgs::Float32 posmotorpasos_msg;
//std_msgs::Int8 btn_msg;

void paso_horario(){         // Pasos a la derecha
 digitalWrite(in4motor_pasos, LOW); 
 digitalWrite(in3motor_pasos, LOW);  
 digitalWrite(in2motor_pasos, LOW);  
 digitalWrite(in1motor_pasos, HIGH);
 nh.spinOnce();  
 delay(retardo); 
 digitalWrite(in4motor_pasos, LOW); 
 digitalWrite(in3motor_pasos, LOW);  
 digitalWrite(in2motor_pasos, HIGH);  
 digitalWrite(in1motor_pasos, LOW);  
 nh.spinOnce();
 delay(retardo); 
 digitalWrite(in4motor_pasos, LOW); 
 digitalWrite(in3motor_pasos, HIGH);  
 digitalWrite(in2motor_pasos, LOW);  
 digitalWrite(in1motor_pasos, LOW);
 nh.spinOnce();  
 delay(retardo); 
 digitalWrite(in4motor_pasos, HIGH); 
 digitalWrite(in3motor_pasos, LOW);  
 digitalWrite(in2motor_pasos, LOW);  
 digitalWrite(in1motor_pasos, LOW);
 nh.spinOnce();  
 delay(retardo);  
}

void paso_antihorario() {        // Pasos a la izquierda
 digitalWrite(in4motor_pasos, HIGH); 
 digitalWrite(in3motor_pasos, LOW);  
 digitalWrite(in2motor_pasos, LOW);  
 digitalWrite(in1motor_pasos, LOW);
 nh.spinOnce();  
 delay(retardo); 
 digitalWrite(in4motor_pasos, LOW); 
 digitalWrite(in3motor_pasos, HIGH);  
 digitalWrite(in2motor_pasos, LOW);  
 digitalWrite(in1motor_pasos, LOW);
 nh.spinOnce();  
 delay(retardo); 
 digitalWrite(in4motor_pasos, LOW); 
 digitalWrite(in3motor_pasos, LOW);  
 digitalWrite(in2motor_pasos, HIGH);  
 digitalWrite(in1motor_pasos, LOW);
 nh.spinOnce();  
 delay(retardo); 
 digitalWrite(in4motor_pasos, LOW); 
 digitalWrite(in3motor_pasos, LOW);  
 digitalWrite(in2motor_pasos, LOW);  
 digitalWrite(in1motor_pasos, HIGH);
 nh.spinOnce();  
 delay(retardo); 
}
  
void motorpasos_apagado() {         // Apagado del Motor a pasos, evita recalentamiento
 digitalWrite(in1motor_pasos, LOW); 
 digitalWrite(in2motor_pasos, LOW);  
 digitalWrite(in3motor_pasos, LOW);  
 digitalWrite(in4motor_pasos, LOW);  
 }

void motorpasos_giro( const std_msgs::Int16& pasos_msg){
  if (pasos_msg.data > 0){
    cont_horario = pasos_msg.data;
    cont_antihorario = 0;
  }
  if (pasos_msg.data < 0){
    cont_antihorario = abs(pasos_msg.data);
    cont_horario = 0;
  }
  if (pasos_msg.data == 0){
    cont_horario = 0;
    cont_antihorario = 0;
  }
  
}

void pwm_wheel_L(const std_msgs::Int8& pwm_L) {
  digitalWrite(in1Left, pwm_L.data >= 0 ? HIGH : LOW);
  digitalWrite(in2Left, pwm_L.data >= 0 ? LOW : HIGH);
  analogWrite(PwmMotorLeft, abs(pwm_L.data)); 
}

void pwm_wheel_R(const std_msgs::Int8& pwm_R) {
  digitalWrite(in1Right, pwm_R.data >= 0 ? LOW : HIGH);
  digitalWrite(in2Right, pwm_R.data >= 0 ? HIGH : LOW);
  analogWrite(PwmMotorRight, abs(pwm_R.data));
}

//ros::Publisher pub_yellow_btn("yellow_btn", &btn_msg);
ros::Publisher pub_posmotorpasos("/get_angle_camera", &posmotorpasos_msg);
ros::Publisher pub_imu("/angle_orientation_robot", &imu_msg);
ros::Subscriber<std_msgs::Int16> sub_motorpasos_giro("/set_angle_camera", &motorpasos_giro);
ros::Subscriber<std_msgs::Int8> sub_pwm_wheel_L("/pwm_wheel_L", &pwm_wheel_L);
ros::Subscriber<std_msgs::Int8> sub_pwm_wheel_R("/pwm_wheel_R", &pwm_wheel_R);

// Main code -----------------------------------------------------------------
void setup(){
  Wire.begin();
  //pinMode(yellow_button, INPUT_PULLUP);
  pinMode(optic_sensor, INPUT);
  pinMode(in1Left, OUTPUT);
  pinMode(in2Left, OUTPUT);
  pinMode(PwmMotorLeft, OUTPUT);
  pinMode(in1Right, OUTPUT);
  pinMode(in2Right, OUTPUT);
  pinMode(PwmMotorRight, OUTPUT); 
  pinMode(in1motor_pasos, OUTPUT);    
  pinMode(in2motor_pasos, OUTPUT);    
  pinMode(in3motor_pasos, OUTPUT);     
  pinMode(in4motor_pasos, OUTPUT);


  // Por alguna razon de limites de hardware arduino uno solo admite hasta 5 nodos sin desincronizarse.
  nh.initNode();
  nh.advertise(pub_imu);
  nh.advertise(pub_posmotorpasos);
  //nh.advertise(pub_yellow_btn); 
  nh.subscribe(sub_motorpasos_giro);
  nh.subscribe(sub_pwm_wheel_L);
  nh.subscribe(sub_pwm_wheel_R);

  compass_x_offset = 177.35;
  compass_y_offset = 123.79;
  compass_z_offset = -33.04;
  compass_x_gainError = 1.12;
  compass_y_gainError = 1.13;
  compass_z_gainError = 1.03;
  compass_init(2);
  //compass_debug = 1;    //descomentar si desea calibrar en otra locacion el IMU
  //compass_offset_calibration(3); //descomentar si desea calibrar en otra locacion el IMU

  //Antes de empezar el bucle del programa se necesita calibrar el motor a pasos a su posicion cero
  while(digitalRead(optic_sensor) == LOW){
    delay(retardo);
    paso_horario();
  }
  motorpasos_apagado();
}

long publisher_timer;
long motorpasos_activate_timer;

void loop(){
  if (millis() > publisher_timer) {
    compass_scalled_reading();
    compass_heading();
    imu_msg.data = bearing;
    pub_imu.publish(&imu_msg);
    //nh.spinOnce();
    //if (digitalRead(13) == HIGH) {
    //  btn_msg.data = 0;
    //} else {
    //  btn_msg.data = 1;
    //}
    //pub_yellow_btn.publish(&btn_msg);
    posmotorpasos_msg.data = pos_global_motorpasos; 
    pub_posmotorpasos.publish(&posmotorpasos_msg);
    publisher_timer = millis() + 100;
  }

  nh.spinOnce();

  if (millis() > motorpasos_activate_timer) {
    
    if (cont_horario > 0){
      motorpasos_active = true;
      paso_horario();
      pos_global_motorpasos++;
      if(pos_global_motorpasos>512) pos_global_motorpasos = 1;
      cont_horario--;
    }
    if (cont_antihorario > 0){
      motorpasos_active = true;
      paso_antihorario();
      pos_global_motorpasos--;
      if(pos_global_motorpasos<0) pos_global_motorpasos = 511;
      cont_antihorario--;
    }
    if (cont_horario==0 and cont_antihorario==0 and motorpasos_active)motorpasos_apagado();
    motorpasos_activate_timer = millis() + 5;
  }
  
  nh.spinOnce();
}
