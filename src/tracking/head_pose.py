import cv2
import numpy as np
from src.utils.angle_buffer import AngleBuffer

_INDICES_POSE = [1, 33, 61, 199, 263, 291]
NOSE_TIP_INDEX = 4
CHIN_INDEX = 152
LEFT_EYE_LEFT_CORNER_INDEX = 33
RIGHT_EYE_RIGHT_CORNER_INDEX = 263
LEFT_MOUTH_CORNER_INDEX = 61
RIGHT_MOUTH_CORNER_INDEX = 291


class HeadPoseEstimator:
    def __init__(self, config: dict) -> None:
        self._user_face_width = config["user_face_width_mm"]
        self._display_threshold = config["head_pose_display_threshold"]
        self._angle_buffer = AngleBuffer(size=config["smoothing_window"])
        self._initial_pitch = None
        self._initial_yaw = None
        self._initial_roll = None
        self._calibrated = False

    def estimate(self, mesh_points: np.ndarray, image_size: tuple) -> tuple:
        scale_factor = self._user_face_width / 150.0
        model_points = np.array([
            (0.0, 0.0, 0.0),
            (0.0, -330.0 * scale_factor, -65.0 * scale_factor),
            (-225.0 * scale_factor, 170.0 * scale_factor, -135.0 * scale_factor),
            (225.0 * scale_factor, 170.0 * scale_factor, -135.0 * scale_factor),
            (-150.0 * scale_factor, -150.0 * scale_factor, -125.0 * scale_factor),
            (150.0 * scale_factor, -150.0 * scale_factor, -125.0 * scale_factor),
        ])
        focal_length = image_size[1]
        center = (image_size[1] / 2, image_size[0] / 2)
        camera_matrix = np.array([
            [focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1],
        ], dtype="double")
        dist_coeffs = np.zeros((4, 1))
        image_points = np.array([
            mesh_points[NOSE_TIP_INDEX],
            mesh_points[CHIN_INDEX],
            mesh_points[LEFT_EYE_LEFT_CORNER_INDEX],
            mesh_points[RIGHT_EYE_RIGHT_CORNER_INDEX],
            mesh_points[LEFT_MOUTH_CORNER_INDEX],
            mesh_points[RIGHT_MOUTH_CORNER_INDEX],
        ], dtype="double")
        success, rotation_vector, translation_vector = cv2.solvePnP(
            model_points, image_points, camera_matrix, dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE
        )
        rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
        projection_matrix = np.hstack((rotation_matrix, translation_vector.reshape(-1, 1)))
        _, _, _, _, _, _, euler_angles = cv2.decomposeProjectionMatrix(projection_matrix)
        pitch, yaw, roll = euler_angles.flatten()[:3]
        pitch = self._normalize_pitch(pitch)
        self._angle_buffer.add([pitch, yaw, roll])
        pitch, yaw, roll = self._angle_buffer.get_average()
        if self._initial_pitch is None:
            self._initial_pitch, self._initial_yaw, self._initial_roll = pitch, yaw, roll
            self._calibrated = True
        if self._calibrated:
            pitch -= self._initial_pitch
            yaw -= self._initial_yaw
            roll -= self._initial_roll
        return pitch, yaw, roll

    def estimate_display(self, mesh_points_3d: np.ndarray, mesh_points: np.ndarray, image_size: tuple) -> dict:
        img_h, img_w = image_size
        head_pose_points_3D = np.multiply(mesh_points_3d[_INDICES_POSE], [img_w, img_h, 1])
        head_pose_points_2D = mesh_points[_INDICES_POSE]
        nose_3D_point = np.multiply(head_pose_points_3D[0], [1, 1, 3000])
        nose_2D_point = head_pose_points_2D[0]
        focal_length = 1 * img_w
        cam_matrix = np.array([
            [focal_length, 0, img_h / 2],
            [0, focal_length, img_w / 2],
            [0, 0, 1],
        ])
        dist_matrix = np.zeros((4, 1), dtype=np.float64)
        hp2d = np.delete(head_pose_points_3D, 2, axis=1).astype(np.float64)
        hp3d = head_pose_points_3D.astype(np.float64)
        success, rot_vec, trans_vec = cv2.solvePnP(hp3d, hp2d, cam_matrix, dist_matrix)
        rotation_matrix, _ = cv2.Rodrigues(rot_vec)
        angles, _, _, _, _, _ = cv2.RQDecomp3x3(rotation_matrix)
        angle_x = angles[0] * 360
        angle_y = angles[1] * 360
        z = angles[2] * 360
        t = self._display_threshold
        if angle_y < -t:
            face_looks = "Left"
        elif angle_y > t:
            face_looks = "Right"
        elif angle_x < -t:
            face_looks = "Down"
        elif angle_x > t:
            face_looks = "Up"
        else:
            face_looks = "Forward"
        nose_3d_projection, _ = cv2.projectPoints(
            nose_3D_point, rot_vec, trans_vec, cam_matrix, dist_matrix
        )
        p1 = nose_2D_point
        p2 = (
            int(nose_2D_point[0] + angle_y * 10),
            int(nose_2D_point[1] - angle_x * 10),
        )
        return {
            "angle_x": angle_x,
            "angle_y": angle_y,
            "z": z,
            "face_looks": face_looks,
            "nose_p1": p1,
            "nose_p2": p2,
        }

    def recalibrate(self) -> None:
        self._initial_pitch = None
        self._initial_yaw = None
        self._initial_roll = None
        self._calibrated = False

    def get_calibrated_angles(self):
        if not self._calibrated:
            return None
        return (self._initial_pitch, self._initial_yaw, self._initial_roll)

    def _normalize_pitch(self, pitch: float) -> float:
        if pitch > 180:
            pitch -= 360
        pitch = -pitch
        if pitch < -90:
            pitch = -(180 + pitch)
        elif pitch > 90:
            pitch = 180 - pitch
        pitch = -pitch
        return pitch
