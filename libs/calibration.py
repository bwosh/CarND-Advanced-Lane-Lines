import numpy as np
class Calibration:
    def __init__(self):
        self.calibrated = False

    def is_calibrated(self):
        return self.calibrated

    def run(self, folder_path: str):
        print("Running calibration...")
        self.calibrated = True # TODO implement calibration

    def undistort(self, gbr_frame: np.ndarray):
        return gbr_frame

    def distort(self, gbr_frame: np.ndarray):
        return gbr_frame