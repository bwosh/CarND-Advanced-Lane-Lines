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

    def get_bird_eye_frame(self, binary_frame:np.ndarray, data, debug=True, inverse=False):
        h,w = binary_frame.shape[0], binary_frame.shape[1]
        img = np.zeros((h,w,3), dtype='uint8')
        if len(binary_frame.shape)==2:
            img[:,:,0] = binary_frame * 255
            img[:,:,1] = binary_frame * 255
            img[:,:,2] = binary_frame * 255
        else:
            img[:,:,:] = binary_frame

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
        
        if not inverse:
            M = cv2.getPerspectiveTransform(src, dst)
        else:
            M = cv2.getPerspectiveTransform(dst, src)

        if debug:
            preview = img.copy()
            warped = cv2.warpPerspective(preview, M, (w, h), flags=cv2.INTER_LINEAR)
            cv2.polylines(warped, dst_pts, True,(0,0,255),5)
            data['03b_birdeye_area_warped'] = warped

            cv2.polylines(preview, src_pts, True,(0,0,255),5)
            data['03a_birdeye_area'] = preview

        warped = cv2.warpPerspective(img, M, (w, h), flags=cv2.INTER_LINEAR)

        return warped 

    def get_weighted_center(self, area):
        index = np.sum(area, axis=0)
        index_weight = np.sum(index)
        if np.isnan(index_weight):
            return None
        index = np.arange(0,len(index))* index
        if index_weight==0:
            return None
        index = np.sum(index)/index_weight
        if np.isnan(index):
            return None 

        index = int(index)
        return index

    def get_lane_boundaries(self,  binary_frame:np.ndarray, data, debug=True):
        left_minx,left_maxx, right_minx, right_maxx = 0,0,0,0

        # Initial processing
        h,w,_ = binary_frame.shape
        preview = binary_frame.copy()
        binary_frame = (binary_frame[:,:,0]/255).astype(int)

        # Measure midpoints of left & right part in lower bottom of an immage
        bottom_half = (binary_frame[w//2:,:])
        histogram = np.sum(bottom_half, axis=0)
        max_left_index = np.argmax(histogram[:w//2])
        max_right_index = np.argmax(histogram[w//2:]) + w//2

        # Line area search parameters
        current_left_x = max_left_index
        current_right_x = max_right_index
        padding = 90
        window_number = 12
        window_height = h//window_number

        left_points = []
        right_points = []

        for window_index in range(window_number):
            x1l = current_left_x - padding
            x2l = current_left_x + padding

            x1r = current_right_x - padding
            x2r = current_right_x + padding

            y1 = h - (window_index+1)*window_height
            y2 = h - window_index*window_height

            left_crop = binary_frame[y1:y2,x1l:x2l]          
            right_crop = binary_frame[y1:y2,x1r:x2r]

            max_left_index = self.get_weighted_center(left_crop)
            max_right_index = self.get_weighted_center(right_crop)

            # Debug images
            if debug:
                cv2.rectangle(preview,(x1l,y1),(x2l,y2),(0,255,0),2)
                cv2.rectangle(preview,(x1r,y1),(x2r,y2),(0,255,0),)

                if max_left_index is not None:
                    cv2.circle(preview, (x1l+max_left_index,y1+(y2-y1)//2), 5, (0,0,255),3)

                if max_right_index is not None:
                    cv2.circle(preview, (x1r+max_right_index,y1+(y2-y1)//2), 5, (0,0,255),3)

            # Shift windows 
            if max_left_index is not None:
                left_points.append((x1l+max_left_index,y1+(y2-y1)//2))
                current_left_x += max_left_index-padding
                if current_left_x < padding:
                    current_left_x = padding

            if max_right_index is not None:
                right_points.append((x1r+max_right_index,y1+(y2-y1)//2))
                current_right_x += max_right_index-padding
                if current_right_x > w-padding:
                    current_right_x = w-padding

        if debug:
            data['04_windows'] = preview

        lfit = None
        if len(left_points)>=3:
            left_points = np.array(left_points)
            # a*x**2 + b*x+ c
            lfit = np.polyfit(left_points[:,1],left_points[:,0], 2)

        rfit=None
        if len(right_points)>=3:
            right_points = np.array(right_points)
            # a*x**2 + b*x+ c
            rfit = np.polyfit(right_points[:,1],right_points[:,0], 2)

        return lfit, rfit

    def get_lane_curvature(self,  binary_frame:np.ndarray, lane_boundaries):
        # TODO get lane curvature
        return None

    def draw_lanes(self, bgr_frame:np.ndarray, lane_boundaries):
        lfit, rfit = lane_boundaries
        ploty = np.linspace(0, bgr_frame.shape[0]-1, bgr_frame.shape[0] )

        if lfit is not None:
            lfitx = lfit[0]*ploty**2 + lfit[1]*ploty + lfit[2]
        if rfit is not None:
            rfitx = rfit[0]*ploty**2 + rfit[1]*ploty + rfit[2]

        padding = 8

        for i in range(ploty.shape[0]):
            y = int(ploty[i])

            # draw right lane
            if rfit is not None:
                xr = int(rfitx[i])
                if xr>=padding and xr<bgr_frame.shape[1]-padding:
                    bgr_frame[y-padding:y+padding,xr-padding:xr+padding,:] = [255,0,0]

            # draw left lane
            if lfit is not None:
                xl = int(lfitx[i])
                if xl>=0 and xl<1280:
                    bgr_frame[y-padding:y+padding,xl-padding:xl+padding,:] = [0,0,255]

            # draw mid area
            if lfit is not None and rfit is not None:
                x_range = np.clip(np.array([xl+padding+1,xr-padding-1]),0,bgr_frame.shape[1]-1)
                if x_range[0]<x_range[1]:
                    bgr_frame[y,x_range[0]:x_range[1],:] = [0,127,0]+ bgr_frame[y,x_range[0]:x_range[1],:]//2

        return bgr_frame

    def post_process(self, bgr_frame:np.ndarray, text:str=None):
        if text:
            cv2.putText(bgr_frame, f"{text}", (10,20), cv2.FONT_HERSHEY_PLAIN, 1, (0,255,0), lineType=cv2.LINE_AA)
        return bgr_frame

    def process_frame(self, bgr_frame:np.ndarray, text:str=None):
        # TODO average with last frame, 
        # TODO reuse lanes if new not found
        # TODO generate all test images output

        # Prepare variables
        frame  = bgr_frame.copy()
        data = {} 

        # Pipeline
        data['00_original'] = frame.copy()

        frame = self.calibration.undistort(frame)
        undistorted = frame.copy()
        data['01_undistorted'] = undistorted

        bin_frame = self.get_binary_map(frame)
        data['02_bin_frame'] = bin_frame.copy()

        bird_eye_frame = self.get_bird_eye_frame(bin_frame, data)
        data['03c_bird_eye_frame'] = bird_eye_frame.copy()

        frame = self.get_bird_eye_frame(frame, data)
        data['03d_bird_eye_frame'] = frame.copy()

        lane_boundaries = self.get_lane_boundaries(bird_eye_frame, data)
        curvature = self.get_lane_curvature(bird_eye_frame, lane_boundaries)

        bframe = self.draw_lanes(bird_eye_frame, lane_boundaries) 
        data['05a_lanes_still_undistorted'] = bframe.copy()

        frame = self.draw_lanes(frame, lane_boundaries) 
        data['05b_lanes_still_undistorted'] = frame.copy()

        frame = self.get_bird_eye_frame(frame, data, debug=False, inverse=True) 
        selection = np.expand_dims((frame[:,:,0] == 0) & (frame[:,:,1] == 0) & (frame[:,:,2] == 0), axis=2)
        frame = selection * undistorted + (1-selection)*frame
        frame = frame.astype('uint8')
        data['06_back_to_perspective'] = frame.copy()

        frame = self.post_process(frame, text=text)
        data['07_post_processed'] = frame.copy()

        return frame, data

