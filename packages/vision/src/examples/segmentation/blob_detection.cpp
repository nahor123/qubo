#include "ros/ros.h"
#include "ros/package.h"
#include "cv.h"
#include "highgui.h"
#include "opencv2/opencv.hpp"


using namespace cv;

int main(int argc, char **argv) {
	ros::init(argc, argv, "hsv_thresholding_example");
	ros::NodeHandle n;

	// open up the video
	VideoCapture stream(ros::package::getPath("vision") + "/data/buoy_backing_up.avi");
	// VideoCapture stream("/home/michael/Documents/ram/data/buoy/20090926063810.avi");

	// VideoCapture stream(0);

	if (!stream.isOpened()) {
		ROS_ERROR("Cannot connect a camera or file! Shuting down...");
		return -1;
	}

	// various stages of images used in processing
	Mat raw_image, thresh_image, thresh_color;

	// blob detector

	// Read image
//	Mat im = imread( "blob.jpg", IMREAD_GRAYSCALE );

	// Set up the detector with default parameters.
	SimpleBlobDetector detector;

	// Detect blobs.
	std::vector<KeyPoint> keypoints;
	detector.detect( stream, keypoints);

	// Draw detected blobs as red circles.
	// DrawMatchesFlags::DRAW_RICH_KEYPOINTS flag ensures the size of the circle corresponds to the size of blob
	Mat stream_with_keypoints;
	drawKeypoints( stream, keypoints, stream_with_keypoints, Scalar(0,0,255), DrawMatchesFlags::DRAW_RICH_KEYPOINTS );

	// Show blobs
	imshow("keypoints", stream_with_keypoints );
	waitKey(0);
//----------------------------------------------------------------------------------------------
	// process frames at 15hz
	ros::Rate loop_rate(15);

	// variables
	int frame_count = 0,  // a frame count is needed to loop the video
	    blur_number = 6,  // the rest are parameters to the algorithms...
	    hue_max     = 100,
	    hue_min     = 0;


	namedWindow("raw image", 2);
	namedWindow("HSV threshold", 2);
	createTrackbar("Hue min", "HSV threshold", &hue_min, 255);
	createTrackbar("Hue max", "HSV threshold", &hue_max, 255);

	// main loop
	while (ros::ok()) {
		// get the next frame
		stream >> raw_image;

		// loop the video if we just got the last frame
		if (stream.get(CV_CAP_PROP_FRAME_COUNT) == ++frame_count) {
			frame_count = 0;
			stream.set(CV_CAP_PROP_POS_AVI_RATIO , 0);
		}

		// make sure we actual got an image
		if (raw_image.empty()) {
			ROS_ERROR("Could not read image from VideoCapture!");
			return -1;
		}

		// HSV thresholding
		cvtColor(raw_image, thresh_image, CV_BGR2HSV);
		GaussianBlur(thresh_image, thresh_image, Size(9, 9), 13);
		inRange(thresh_image, Scalar(0, hue_min, 0), Scalar(255, hue_max, 255), thresh_image);
		GaussianBlur(thresh_image, thresh_image, Size(9, 9), 13);
		thresh_color = Scalar::all(0);
		// raw_image.copyTo(thresh_color, thresh_image);

		// Blob dedection
		// detector
		blob_detector.detect(thresh_image, keypoints);
		std::cout << "keypoints: " << keypoints.size() << "\n";
		drawKeypoints(raw_image, keypoints, raw_image, Scalar(0,0,255), DrawMatchesFlags::DRAW_RICH_KEYPOINTS );

		// display images is seperate windows
		imshow("raw image", raw_image);
		imshow("HSV threshold", thresh_image);

		// needed for the opencv GUI
		waitKey(1);

		// make sure we run at 15hz
		loop_rate.sleep();
	}

	destroyWindow("Image");
	return 0;
}
