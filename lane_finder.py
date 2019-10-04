import cv2
import numpy as np
from tqdm import tqdm

from libs.lane_pipeline import LanePipeline

class LaneFinder:
    def __init__(self, input_path: str, output_path: str, calibration_path: str, mode: str):
        self.input_path = input_path
        self.output_path = output_path
        self.calibration_path = calibration_path
        self.mode = mode
        self.lane_pipeline = LanePipeline()

    def process(self, show_progress=True):
        if self.mode == 'video':
            self.__process_video()

        if self.mode == 'image':
            self.__process_image()

    def __process_video(self):
        frame_index = 0
        cap = cv2.VideoCapture(self.input_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        out = None
        all_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
 
        if not cap.isOpened(): 
            print("Could not open:", self.input_path)

        with tqdm(total = all_frames) as p:
            while(cap.isOpened()):
                ret, frame = cap.read()
                if ret:
                    if out is None:
                        out = cv2.VideoWriter(self.output_path, cv2.VideoWriter_fourcc('M','J','P','G'), fps, (frame.shape[1],frame.shape[0]))

                    processed = self.__process_frame(frame, text=f"{frame_index}")
                    out.write(processed)
                    frame_index+=1
                    p.update(1)
                else:
                    break
 
        out.release()
        cap.release() 

    def __process_image(self):
        img = cv2.imread(self.input_path)
        output = self.__process_frame(img, text="IMAGE")
        cv2.imwrite(self.output_path, output)
        print(f"Saved: {self.output_path}")

    def __process_frame(self, gbr_frame: np.ndarray, text = None):
        if not self.lane_pipeline.calibration.is_calibrated():
            self.lane_pipeline.calibrate(self.calibration_path)

        original, data, result = self.lane_pipeline.process_frame(gbr_frame, text=text)

        return result 