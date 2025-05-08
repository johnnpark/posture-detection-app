import cv2
import mediapipe as mp
import math

class PostureDetector:
    def __init__(self,
                 mode=False,
                 upBody=False,
                 smooth=True,
                 detectCon=0.7,
                 trackCon=0.7):
        self.mode = mode
        self.upBody = upBody
        self.smooth = smooth
        self.detectCon = detectCon
        self.trackCon = trackCon

        self.mpDraw = mp.solutions.drawing_utils
        self.mpPose = mp.solutions.pose
        self.pose = self.mpPose.Pose(
            static_image_mode=self.mode,
            model_complexity=2,
            smooth_landmarks=True,
            enable_segmentation=False,
            min_detection_confidence=self.detectCon,
            min_tracking_confidence=self.trackCon
        )

        # Calibration fields
        self.calibrated_z = None
        self.calibrating = False
        self.calibration_data = []
        self.calibration_frames = 60  # ~2 seconds at 30 FPS

    def findPose(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(imgRGB)

        if self.results.pose_landmarks:
            if draw:
                self.mpDraw.draw_landmarks(
                    img, self.results.pose_landmarks, self.mpPose.POSE_CONNECTIONS)
        return img

    def findPosition(self, img, draw=True):
        lmList = []
        if self.results.pose_landmarks:
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                cz = (lm.z)
                lmList.append([id, cz, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 10, (255, 0, 0), cv2.FILLED)
        return lmList

    def get_point(self, lmList, id):
        for item in lmList:
            if item[0] == id and len(item) >= 4:
                return item[2], item[3]  # (x, y)
        return None

    def calculate_angle(self, a, b, c):
        ang = math.degrees(
            math.atan2(c[1] - b[1], c[0] - b[0]) -
            math.atan2(a[1] - b[1], a[0] - b[0])
        )
        return abs(ang)

    def calibrate(self, lmList):
        """ Collect Z values during calibration phase """
        if lmList and len(lmList) > 0:
            nose_z = lmList[0][1]
            self.calibration_data.append(nose_z)

            if len(self.calibration_data) >= self.calibration_frames:
                self.calibrated_z = sum(self.calibration_data) / len(self.calibration_data)
                print(f"✅ Calibration complete. Calibrated Z: {self.calibrated_z:.4f}")
                self.calibrating = False

    def detectForwardHead(self, lmList, offset=0.05):
        """
        Use dynamic Z-depth based on calibration.
        Triggers 'bad posture' if nose is too far forward (i.e., more negative).
        """
        if self.calibrating:
            self.calibrate(lmList)
            return False

        if lmList and len(lmList) > 0 and self.calibrated_z is not None:
            nose_z = lmList[0][1]
            print(f"Nose Z: {nose_z:.4f}, Calibrated Z: {self.calibrated_z:.4f}")
            return nose_z < (self.calibrated_z - offset)
        return False

# Optional main test loop
def main():
    cap = cv2.VideoCapture(0)
    detector = PostureDetector()
    detector.calibrating = True
    detector.calibration_data = []

    while True:
        success, img = cap.read()
        img = detector.findPose(img)
        lmList = detector.findPosition(img)

        if detector.detectForwardHead(lmList):
            cv2.putText(img, "Forward Head Detected!", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
            print("⚠️ Forward Head Detected!")
        else:
            cv2.putText(img, "Good Posture", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            print("Good or Calibrating...")

        cv2.imshow("Live Camera", img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
