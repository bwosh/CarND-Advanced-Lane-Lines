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

                    processed, _ = self.__process_frame(frame, text=f"{frame_index}")
                    out.write(processed)
                    frame_index+=1
                    p.update(1)
                else:
                    break
 
        out.release()
        cap.release() 

    def __process_image(self):
        img = cv2.imread(self.input_path)
        output, data = self.__process_frame(img, text="IMAGE")
        
        cv2.imwrite(self.output_path, output)
        print(f"Saved: {self.output_path}")

        for k in data:
            immediate_file = self.output_path.replace(".jpg",f"_{k}.jpg")
            self.__save_immediate_image(immediate_file, data[k])
            print(f"Saved: {immediate_file}")

    def __save_immediate_image(self, filepath, data: np.ndarray):
        to_save = None
        if str(data.dtype)=='bool':
            data = data.astype('uint8') * 255

        if str(data.dtype)=='uint8':
            if len(data.shape)==3 and data.shape[2]==3:
                to_save = data
            if len(data.shape)==2:
                to_save = np.repeat(np.expand_dims(data,axis=2), 3, axis=2)

        if to_save is None:      
            raise Exception(f"Unknown data format:{data.dtype}, {data.shape}")

        cv2.imwrite(filepath, to_save)

    def __process_frame(self, bgr_frame: np.ndarray, text = None):
        if not self.lane_pipeline.calibration.is_calibrated():
            self.lane_pipeline.calibrate(self.calibration_path)

        return self.lane_pipeline.process_frame(bgr_frame, text=text)