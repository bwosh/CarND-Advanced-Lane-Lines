import cv2
import numpy as np
from libs.calibration import Calibration

class LanePipeline:
    def __init__(self):
        self.calibration = Calibration()

    def calibrate(self, folder_path: str):
        self.calibration.run(folder_path)

    def process_frame(self, gbr_frame:np.ndarray, text:str=None):
        frame  = gbr_frame.copy()

        if text:
            cv2.putText(frame, f"{text}", (10,20), cv2.FONT_HERSHEY_PLAIN, 1, (0,255,0), lineType=cv2.LINE_AA)
        # TODO: Not implemented 
        data = []

        return gbr_frame, data, frame

