import cv2  # pip install opencv-python
from deepface import DeepFace  # pip install deepface
import time  # For FPS calculation

# Load the face cascade model
faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Initialize webcam
cap = cv2.VideoCapture(1)
if not cap.isOpened():
    cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise IOError("Camera unable to open!")

# Variables for FPS calculation
frame_count = 0
start_time = time.time()

while True:
    ret, frame = cap.read()  # Capture a frame from the webcam
    if not ret:
        print("Failed to capture frame from camera. Exiting...")
        break

    # Downsample frame to improve performance
    small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)

    # Convert frame to grayscale for face detection
    gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4)

    # Analyze emotions using DeepFace every few frames
    if frame_count % 5 == 0:  # Skip DeepFace for some frames
        try:
            if len(faces) > 0:  # Proceed only if faces are detected
                result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
                dominant_emotion = result[0]['dominant_emotion']
            else:
                dominant_emotion = "No Face Detected"
        except Exception as e:
            print("Error in DeepFace analysis:", e)
            dominant_emotion = "Analysis Error"

    # Draw rectangles around detected faces
    for (x, y, w, h) in faces:
        x, y, w, h = x * 2, y * 2, w * 2, h * 2  # Adjust for downscaling
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Display the dominant emotion
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(frame,
                dominant_emotion,
                (10, 50),  # Position of the text
                font, 1,  # Font scale
                (0, 255, 0), 2,  # Text color and thickness
                cv2.LINE_AA)

    # FPS Calculation
    frame_count += 1
    elapsed_time = time.time() - start_time
    fps = frame_count / elapsed_time
    cv2.putText(frame,
                f"FPS: {fps:.2f}",
                (10, 100),  # Position for FPS display
                font, 1,
                (255, 0, 0), 2,
                cv2.LINE_AA)

    # Display the video feed
    cv2.imshow('Emotion Detection', frame)

    # Exit on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
