import cv2
import numpy as np
from libs.calibration import Calibration

class LanePipeline:
    def __init__(self):
        self.calibration = Calibration()

    def calibrate(self, folder_path: str):
        self.calibration.run(folder_path)

    def get_binary_map(self, gbr_frame:np.ndarray):
        grayscale = cv2.cvtColor(gbr_frame, cv2.COLOR_BGR2GRAY)
        return grayscale>128 # TODO implement sobel ans saturation threshold

    def get_bird_eye_frame(self, binary_frame:np.ndarray):
        return binary_frame # TODO implement bir eye transformtion

    def get_lane_boundaries(self,  binary_frame:np.ndarray):
        left_minx,left_maxx, right_minx, right_maxx = 0,0,0,0
        # TODO impement lane boundaries detections
        return [left_minx,left_maxx, right_minx, right_maxx]

    def get_lane_curvature(self,  binary_frame:np.ndarray, lane_boundaries):
        # TODO get lane curvature
        return None

    def draw_lanes(self, gbr_frame:np.ndarray, lane_boundaries):
        # TODO draw lanes
        return gbr_frame

    def post_process(self, gbr_frame:np.ndarray, text:str=None):
        if text:
            cv2.putText(gbr_frame, f"{text}", (10,20), cv2.FONT_HERSHEY_PLAIN, 1, (0,255,0), lineType=cv2.LINE_AA)
        return gbr_frame

    def process_frame(self, gbr_frame:np.ndarray, text:str=None):
        # Prepare variables
        frame  = gbr_frame.copy()
        data = {} 

        # Pipeline
        data['00_original'] = frame.copy()

        frame = self.calibration.undistort(frame)
        data['01_undistorted'] = frame.copy()

        bin_frame = self.get_binary_map(frame)
        data['02_bin_frame'] = bin_frame.copy()

        bird_eye_frame = self.get_bird_eye_frame(bin_frame)
        data['03_bird_eye_frame'] = bird_eye_frame.copy()

        lane_boundaries = self.get_lane_boundaries(bird_eye_frame)
        curvature = self.get_lane_curvature(bird_eye_frame, lane_boundaries)

        frame = self.draw_lanes(frame, lane_boundaries)
        data['04_lanes_still_undistorted'] = frame.copy()

        frame = self.calibration.distort(frame)
        data['05_lanes_on_original'] = frame.copy()

        frame = self.post_process(frame, text=text)

        return frame, data

