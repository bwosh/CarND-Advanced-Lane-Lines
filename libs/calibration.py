import cv2
import numpy as np
import os

class Calibration:
    def __init__(self, chessboardNx=9, chessboardNy=6):
        self.calibrated = False
        self.chessboardNx = chessboardNx
        self.chessboardNy = chessboardNy

    def is_calibrated(self):
        return self.calibrated

    def run(self, folder_path: str, verbose=False):
        print("Running calibration...")
        calibration_files = list(os.listdir(folder_path))
        calibration_files.sort()

        imgpoints = np.zeros((self.chessboardNx * self.chessboardNy,3), np.float32)
        imgpoints[:,:2] = np.mgrid[0:self.chessboardNx,0:self.chessboardNy].T.reshape(-1,2)

        cal_imgpoints=[]
        cal_corners = []

        for file in calibration_files:
            img = cv2.imread(os.path.join(folder_path, file))
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            ret, corners = cv2.findChessboardCorners(gray, (self.chessboardNx, self.chessboardNy), None)
            if ret and gray.shape[1]==1280 and gray.shape[0]==720:
                if verbose:
                    print("Calibration file:", file, corners.shape, img.shape)
                cal_corners.append(corners)
                cal_imgpoints.append(imgpoints)
            else:
                if verbose:
                    print("BROKEN calibration file:", file)

        cal_corners = np.array(cal_corners)
        cal_imgpoints = np.array(cal_imgpoints)

        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(cal_imgpoints, cal_corners, gray.shape[::-1], None, None)

        self.mtx = mtx
        self.dist = dist

        self.calibrated = True

    def undistort(self, bgr_frame: np.ndarray):
        undist = cv2.undistort(bgr_frame, self.mtx, self.dist, None, self.mtx)
        return undist