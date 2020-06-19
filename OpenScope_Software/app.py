from importlib import import_module
import os
from flask import Flask, render_template, Response, jsonify
import RPi.GPIO as GPIO
import time


# import camera driver
if os.environ.get('CAMERA'):
    Camera = import_module('camera_' + os.environ['CAMERA']).Camera
else:
    from camera import Camera

# Raspberry Pi camera module (requires picamera package)
# from camera_pi import Camera

app = Flask(__name__)

servo_inf_PIN = 17
servo_sup_PIN=27
GPIO.setmode(GPIO.BCM)
GPIO.setup(servo_inf_PIN, GPIO.OUT)
GPIO.setup(servo_sup_PIN, GPIO.OUT)
p_inf = GPIO.PWM(servo_inf_PIN, 50) # GPIO 17 for PWM with 50Hz
p_sup = GPIO.PWM(servo_sup_PIN, 50)
a_inf = 7
a_sup = 7
p_inf.start(0)
p_sup.start(0)

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/commande/<button_id>')
def commande(button_id):
    global a_sup
    global a_inf
    global p_sup
    global p_inf
    print(a_sup,a_inf)


    print(button_id)
    if button_id =='bas':
       if a_sup <7:
          print('bas')
          a_sup+=0.2
          p_sup.ChangeDutyCycle(a_sup)
          time.sleep(0.2)
          p_sup.ChangeDutyCycle(0)
    if button_id =='haut':
        if a_sup >5.7:
           a_sup-=0.2
           p_sup.ChangeDutyCycle(a_sup)
           time.sleep(0.2)
           p_sup.ChangeDutyCycle(0)
    if button_id =='gauche':
       if a_inf<12:
          print('gauche')
          a_inf+=0.2
          p_inf.ChangeDutyCycle(a_inf)
          time.sleep(0.3)
          p_inf.ChangeDutyCycle(0)

    if button_id =='droite':
       if a_inf>2:
          print('droite')
          a_inf-=0.2
          p_inf.ChangeDutyCycle(a_inf)
          time.sleep(0.3)
          p_inf.ChangeDutyCycle(0)

    return jsonify(file=a_sup)

if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
