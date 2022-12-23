import cv2
import mediapipe as mp

def detect_hunchback(filename: str) -> tuple[str, bool]:
    """
    @param  filename 圖片檔案路徑
    @return str      姿勢骨架圖片檔案路徑
    @return bool     是否駝背
    """
    mp_drawing = mp.solutions.drawing_utils          # mediapipe 繪圖方法
    mp_drawing_styles = mp.solutions.drawing_styles  # mediapipe 繪圖樣式
    mp_pose = mp.solutions.pose                      # mediapipe 姿勢偵測

    img = cv2.imread(filename, cv2.IMREAD_COLOR)

    # 啟用姿勢偵測
    with mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5) as pose:

        # 縮小尺寸，加快演算速度
        img2 = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)   # 將 BGR 轉換成 RGB
        results = pose.process(img2)                  # 取得姿勢偵測結果

        keypoints = []
        for data_point in results.pose_landmarks.landmark:
            keypoints.append({
                'X': data_point.x,
                'Y': data_point.y,
                'Z': data_point.z,
                'Visibility': data_point.visibility,
            })

        if keypoints[12]['Visibility']<keypoints[11]['Visibility'] and keypoints[24]['Visibility']<keypoints[23]['Visibility']:
            a=12
            b=24
        else:
            a=11
            b=23

        x_dis=abs(keypoints[a]['X']-keypoints[b]['X'])
        y_dis=abs(keypoints[a]['Y']-keypoints[b]['Y'])
        tan_theta=x_dis/y_dis

        # 根據姿勢偵測結果，標記身體節點和骨架
        mp_drawing.draw_landmarks(img, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())

        output_filename = "./static/posture_image/pos_recong.jpg"
        cv2.imwrite(output_filename, img)

    return (output_filename, tan_theta > 0.1)
