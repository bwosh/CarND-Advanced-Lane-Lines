import cv2
import numpy as np
from tqdm import tqdm

from libs.lane_pipeline import LanePipeline

class LaneFinder:
    def __init__(self, input_path: str, output_path: str, calibration_path: str, mode: str, multiview: bool):
        self.input_path = input_path
        self.output_path = output_path
        self.calibration_path = calibration_path
        self.mode = mode
        self.lane_pipeline = LanePipeline()
        self.multiview = multiview

    def process(self, show_progress=True):
        if self.mode == 'video':
            self.__process_video()

        if self.mode == 'image':
            self.__process_image()

    def __merge_frames(self, key_frame, dict_of_frames):
        output = np.zeros((key_frame.shape[0],key_frame.shape[1]*2,3),dtype='uint8')
        output[:,:key_frame.shape[1],:] = key_frame

        for keyid, key in enumerate(dict_of_frames.keys()):
            y = keyid // 4
            x = keyid % 4
            ws = key_frame.shape[1]//4
            hs = key_frame.shape[0]//4

            miniframe = dict_of_frames[key]
            if len(miniframe.shape)==2:
                miniframe = np.dstack((miniframe, miniframe, miniframe))
            if str(miniframe.dtype) == 'bool':
                miniframe = miniframe.astype('uint8')*255
            miniframe = cv2.pyrDown(cv2.pyrDown(miniframe))

            output[y*hs:y*hs+miniframe.shape[0],
                   key_frame.shape[1]+x*ws:key_frame.shape[1]+x*ws+miniframe.shape[1]] = miniframe

        return output

    def __process_video(self):
        # TODO add split video mode
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
                        width = frame.shape[1]
                        if self.multiview:
                            width *= 2
                        out = cv2.VideoWriter(self.output_path, cv2.VideoWriter_fourcc('M','J','P','G'), fps, (width,frame.shape[0]))

                    processed, data = self.__process_frame(frame, text=f"{frame_index}")
                    if self.multiview:
                        processed = self.__merge_frames(processed, data)

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

        to_save = cv2.pyrDown(cv2.pyrDown(to_save))
        cv2.imwrite(filepath, to_save)

    def __process_frame(self, bgr_frame: np.ndarray, text = None):
        if not self.lane_pipeline.calibration.is_calibrated():
            self.lane_pipeline.calibrate(self.calibration_path)

        return self.lane_pipeline.process_frame(bgr_frame, text=text)