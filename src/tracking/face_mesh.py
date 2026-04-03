import cv2
import numpy as np
import mediapipe as mp


class FaceMeshTracker:
    def __init__(self, config: dict) -> None:
        self._face_mesh = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=config["min_detection_confidence"],
            min_tracking_confidence=config["min_tracking_confidence"],
        )

    def process(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_h, img_w = frame.shape[:2]
        results = self._face_mesh.process(rgb)
        if not results.multi_face_landmarks:
            return None
        mesh_points = np.array(
            [np.multiply([p.x, p.y], [img_w, img_h]).astype(int)
             for p in results.multi_face_landmarks[0].landmark]
        )
        mesh_points_3d = np.array(
            [[n.x, n.y, n.z] for n in results.multi_face_landmarks[0].landmark]
        )
        return mesh_points, mesh_points_3d

    def close(self) -> None:
        self._face_mesh.close()
