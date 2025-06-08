# test_stretch_detect.py
import cv2
import mediapipe as mp
import time

mp_pose = mp.solutions.pose
drawing = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)

detected_start_time = None
stretch_confirmed = False
min_duration = 0.5

with mp_pose.Pose(min_detection_confidence=0.5) as pose:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frame_rgb)
        annotated_frame = frame.copy()

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            h, w, _ = frame.shape
            lw = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
            rw = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]
            nose = landmarks[mp_pose.PoseLandmark.NOSE]

            lw_point = (int(lw.x * w), int(lw.y * h))
            rw_point = (int(rw.x * w), int(rw.y * h))
            nose_point = (int(nose.x * w), int(nose.y * h))

            stretch_condition = lw.y < nose.y and rw.y < nose.y

            if stretch_condition:
                if detected_start_time is None:
                    detected_start_time = time.time()
                elif time.time() - detected_start_time >= min_duration:
                    stretch_confirmed = True
            else:
                detected_start_time = None

            if stretch_confirmed:
                cv2.putText(annotated_frame, "✅ Stretch Confirmed!", (30, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)
            else:
                cv2.putText(annotated_frame, "Raise both hands above head", (30, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)

            cv2.circle(annotated_frame, lw_point, 10, (255, 0, 0), -1)
            cv2.circle(annotated_frame, rw_point, 10, (0, 255, 0), -1)
            cv2.circle(annotated_frame, nose_point, 10, (0, 255, 255), -1)
            cv2.line(annotated_frame, lw_point, nose_point, (255, 255, 255), 2)
            cv2.line(annotated_frame, rw_point, nose_point, (255, 255, 255), 2)

            drawing.draw_landmarks(annotated_frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            if stretch_confirmed:
                print("Stretch Detected!")
                break

        cv2.imshow("Stretch Detection", annotated_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()