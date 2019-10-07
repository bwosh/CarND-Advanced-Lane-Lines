import cv2
import numpy as np
from libs.calibration import Calibration

class LanePipeline:
    def __init__(self):
        self.calibration = Calibration()

    def calibrate(self, folder_path: str):
        self.calibration.run(folder_path)

    def get_binary_map(self, bgr_frame:np.ndarray):
        hls = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2HLS)
        r = bgr_frame[:,:,2]
        s = hls[:,:,2]

        r_thresh = (190, 255)
        r_binary = (r>r_thresh[0]) & (r<=r_thresh[1])

        s_thresh = (90,255)
        s_binary = (s>s_thresh[0]) & (s<=s_thresh[1])

        return s_binary*r_binary

    def get_bird_eye_frame(self, binary_frame:np.ndarray, debug=True):
        h,w = binary_frame.shape

        # Source Top/Bottom Left/Right points
        bl = [w//7, h]
        br = [w-w//7, h]
        tl = [w//2-w//20,h//2+h//7]
        tr = [w//2+w//20,h//2+h//7]
        src = np.array([tl,tr, br, bl], dtype=np.float32)
        src_pts = np.array([[tl,tr, br, bl]], dtype=np.int64)

        # Target Top/Bottom Left/Right points
        t_bl = [w//6, h]
        t_br = [w-w//6, h]
        t_tl = [w//6,0]
        t_tr = [w-w//6,0]
        dst = np.array([t_tl,t_tr, t_br, t_bl], dtype=np.float32)
        dst_pts = np.array([[t_tl,t_tr, t_br, t_bl]], dtype=np.int64)
        print(src.shape, src.dtype)
        print(dst.shape, dst.dtype)
        
        M = cv2.getPerspectiveTransform(src, dst)

        img = np.zeros((h,w,3), dtype='uint8')
        img[:,:,0] = binary_frame * 255
        img[:,:,1] = binary_frame * 255
        img[:,:,2] = binary_frame * 255

        if debug:
            preview = img.copy()
            warped = cv2.warpPerspective(preview, M, (w, h), flags=cv2.INTER_LINEAR)
            cv2.polylines(warped, dst_pts, True,(0,0,255),5)
            cv2.imwrite("temp_birdline_area_warped.jpg",warped)

            cv2.polylines(preview, src_pts, True,(0,0,255),5)
            cv2.imwrite("temp_birdline_area_1.jpg",preview)

        warped = cv2.warpPerspective(img, M, (w, h), flags=cv2.INTER_LINEAR)

        return warped 

    def get_lane_boundaries(self,  binary_frame:np.ndarray):
        left_minx,left_maxx, right_minx, right_maxx = 0,0,0,0
        # TODO impement lane boundaries detections
        return [left_minx,left_maxx, right_minx, right_maxx]

    def get_lane_curvature(self,  binary_frame:np.ndarray, lane_boundaries):
        # TODO get lane curvature
        return None

    def draw_lanes(self, bgr_frame:np.ndarray, lane_boundaries):
        # TODO draw lanes
        return bgr_frame

    def post_process(self, bgr_frame:np.ndarray, text:str=None):
        if text:
            cv2.putText(bgr_frame, f"{text}", (10,20), cv2.FONT_HERSHEY_PLAIN, 1, (0,255,0), lineType=cv2.LINE_AA)
        return bgr_frame

    def process_frame(self, bgr_frame:np.ndarray, text:str=None):
        # Prepare variables
        frame  = bgr_frame.copy()
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

        frame = self.post_process(frame, text=text)
        data['05_post_processed'] = frame.copy()

        return frame, data

