from django.shortcuts import render

# Create your views here.
import cv2
from django.http import StreamingHttpResponse

import cv2
from django.http import StreamingHttpResponse
from ultralytics import YOLO

model = YOLO("./weights/best.pt")

def gen_frames():
    cap = cv2.VideoCapture(0)  # webcam
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    
    if not cap.isOpened():
        raise IOError("Không thể mở camera")

    while True:
        success, frame = cap.read()
        if not success:
            break

        # Debug: Print actual frame dimensions
        actual_height, actual_width = frame.shape[:2]
        # print(f"Frame dimensions: {actual_width}x{actual_height}")

        # Nhận diện bằng YOLO
        results = model(frame)

        for r in results:
            # Option 1: Process boxes individually
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = box.conf[0].item()

                if conf > 0.5:
                    # Corrected labels: left to right = A, B, C
                    # Adjust thresholds based on your frame size
                    if x1 < actual_width * 0.3:  # Left third of frame
                        label = "C"
                        color = (255, 36, 0)  # Red
                    elif x1 > actual_width * 0.6:  # Right third of frame
                        label = "A"
                        color = (0, 255, 255)  # Yellow
                    else:  # Middle third
                        label = "B"
                        color = (0, 255, 0)  # Green

                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(frame, label, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                    
                    # Debug: Print the detection info
                    # print(f"Detected box: x1={x1}, position={x1/actual_width:.2f}, label={label}")

        # Mã hóa ảnh trả về
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        # Stream MJPEG
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

def gen_frames_2():
    cap = cv2.VideoCapture(1)

    # Set resolution to 1920x1080 (as in your code)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    if not cap.isOpened():
        raise IOError("Không thể mở camera")

    while True:
        success, frame = cap.read()
        if not success:
            break

        # Debug: Print actual frame dimensions
        actual_height, actual_width = frame.shape[:2]
        # print(f"Camera 2 dimensions: {actual_width}x{actual_height}")

        # Mã hóa ảnh trả về
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        # Stream MJPEG
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

def camera_feed(request):
    return StreamingHttpResponse(gen_frames(), content_type='multipart/x-mixed-replace; boundary=frame')
def camera_feed_2(request):
    return StreamingHttpResponse(gen_frames_2(), content_type='multipart/x-mixed-replace; boundary=frame')
