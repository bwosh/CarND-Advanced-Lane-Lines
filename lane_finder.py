import cv2
import numpy as np
from tqdm import tqdm

from libs.lane_pipeline import LanePipeline

class LaneFinder:
    def __init__(self, input_path: str, output_path: str, mode: str):
        self.input_path = input_path
        self.output_path = output_path
        self.mode = mode
        self.lane_pipeline = LanePipeline()

    def process(self, show_progress=True):
        if self.mode == 'video':
            self.__process_video()

        if self.mode == 'image':
            self.__process_image()

    def __process_video(self):
        pass # TODO: Not implemented
        frame_index = 0

    def __process_image(self):
        img = cv2.imread(self.input_path)
        output = self.__process_frame(img)
        cv2.imwrite(self.output_path, output)

    def __process_frame(self, gbr_frame: np.ndarray):
        return gbr_frame # TODO: Not implemented 