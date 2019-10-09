## Advanced Lane Finding

### Work in progress...



The goals of this project are the following:

* Compute the camera calibration matrix and distortion coefficients given a set of chessboard images.
* Apply a distortion correction to raw images.
* Use color transforms, gradients, etc., to create a thresholded binary image.
* Apply a perspective transform to rectify binary image ("birds-eye view").
* Detect lane pixels and fit to find the lane boundary.
* Determine the curvature of the lane and vehicle position with respect to center.
* Warp the detected lane boundaries back onto the original image.
* Output visual display of the lane boundaries and numerical estimation of lane curvature and vehicle position.


The pipeline
---

*This is description of how the processing is made with sample results on two sample input frames.*

1. Take RAW image  
![Raw image](examples/straight_lines1_00_original.jpg "Raw image")![Raw image](examples/test1_00_original.jpg "Raw image")

2. Undistort image (after processing sample chessboard images on given camera)  
![Undistorted image](examples/straight_lines1_01_undistorted.jpg "Undistorted image")![Undistorted image](examples/test1_01_undistorted.jpg "Undistorted image")  

3. Binarize image using color transforms (take Red value from RGB channels and combine it with Saturation channel of HLS color space)  
![Binarized image](examples/straight_lines1_02_bin_frame.jpg "Binarized image")![Binarized image](examples/test1_02_bin_frame.jpg "Binarized image")  

4. Apply trapezoidal Region of Interest (ROI) shape of expected straigt lane  
![Trapezoid image](examples/straight_lines1_03a_birdeye_area.jpg "Trapezoid image")![Trapezoid image](examples/test1_03a_birdeye_area.jpg "Trapezoid image")  

5. Perspective transform of ROI to bird-eye view.  
![Bird-eye  image](examples/straight_lines1_03b_birdeye_area_warped.jpg "Bird-eye image")![Bird-eye  image](examples/test1_03b_birdeye_area_warped.jpg "Bird-eye image")  

6. Use binary image without ROI highlight for further processing  
![Raw image](examples/straight_lines1_03c_bird_eye_frame.jpg "Raw image")![Raw image](examples/test1_03c_bird_eye_frame.jpg "Raw image")  

7. Starting from bottom search for centers of mass inside rectangular areas (while shifting window to new center)  
![Raw image](examples/straight_lines1_04_windows.jpg "Raw image")![Raw image](examples/test1_04_windows.jpg "Raw image")  

8. Basing on centers of lanes inside areas find quadratic function that matches the points and plot the lanes  
![Raw image](examples/straight_lines1_05a_lanes_still_undistorted.jpg "Raw image")![Raw image](examples/test1_05a_lanes_still_undistorted.jpg "Raw image") 

9. Perform lane drawing on bird-eye view of the original image  
![Raw image](examples/straight_lines1_05b_lanes_still_undistorted.jpg "Raw image")![Raw image](examples/test1_05b_lanes_still_undistorted.jpg "Raw image") 

10. Invert perspective transform and merge result with undistorted part of images that were out-of bounds of bird-eye view  
![Raw image](examples/straight_lines1_06_back_to_perspective.jpg "Raw image")![Raw image](examples/test1_06_back_to_perspective.jpg "Raw image") 

(more to come...)
