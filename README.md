## Advanced Lane Finding

### Work in progress...


The Project
---

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

*This is description of how the processing is made with sample results on one inut frame.*

1. Take RAW image  
![Raw image](examples/00.jpg "Raw image")

2. Undistort image (after processing sample chessboard images)
![Undistorted image](examples/01.jpg "Undistorted image")

3. Binarize image using color transforms (take Red value from RGB channels and combine it with Saturation channel of HLS color space)
![Binarized image](examples/02.jpg "Binarized image")

4. Apply trapezoidal Region of Interest (ROI) shape of expected straigt lane
![Trapezoid image](examples/03.jpg "Trapezoid image")

5. Perspective transform of ROI to bird-eye view.
![Bird-eye  image](examples/04.jpg "Bird-eye image")

6. Use binary image withour ROI highlight for further processing
![Raw image](examples/05.jpg "Raw image")

(more to come...)
