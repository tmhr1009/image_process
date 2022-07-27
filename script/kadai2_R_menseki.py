#!/usr/bin/env python

import rospy
from sensor_msgs.msg import Image , CompressedImage
from cv_bridge import CvBridge
import cv2
import numpy as np
import math
import pyocr
import pyocr.builders
from PIL import Image
from std_msgs.msg import Int8

tools = pyocr.get_available_tools()
tool = tools[0]

p1 = np.array([570, 275])
p2 = np.array([730, 275])
p3 = np.array([558, 367])
p4 = np.array([742, 370])

src = np.float32([p1, p2, p3, p4])
dst = np.float32([[0,0],[100,0],[0,100],[100,100]])

M = cv2.getPerspectiveTransform(src, dst)
kernel = np.ones((3, 3), np.uint8)

pub2=rospy.Publisher('img_r',Int8,queue_size=10)

def process_image(msg):
    try:
	b=0
        bridge = CvBridge()
        orig = bridge.compressed_imgmsg_to_cv2(msg, "bgr8")


 	hsvLower_y = np.array([30, 50, 80])    #20,40
 	hsvUpper_y = np.array([100, 240 ,240])   #240,240
     
 	hsvLower_m = np.array([60, 0, 0])   
 	hsvUpper_m = np.array([100, 240,240])  
     
 	hsvLower_c = np.array([106, 10, 0])    
 	hsvUpper_c = np.array([176, 240 ,240])

        hsv = cv2.cvtColor(orig, cv2.COLOR_BGR2HSV)
	my_debug = cv2.warpPerspective(orig, M,(100,100))
	cv2.imshow('img_R',my_debug)

        hsv_mask_y = cv2.inRange(orig, hsvLower_y, hsvUpper_y)
 	hsv_mask_m = cv2.inRange(orig, hsvLower_m, hsvUpper_m)
 	hsv_mask_c = cv2.inRange(orig, hsvLower_c, hsvUpper_c)
	
	ret, img_y = cv2.threshold(hsv_mask_y, 100, 255, cv2.THRESH_BINARY)
        img_y = cv2.erode(hsv_mask_y,kernel,iterations = 3)
	ret, img_c = cv2.threshold(hsv_mask_c, 100, 255, cv2.THRESH_BINARY)
        img_c = cv2.erode(hsv_mask_c,kernel,iterations = 3)
	ret, img_m = cv2.threshold(hsv_mask_m, 100, 255, cv2.THRESH_BINARY)
        img_m = cv2.erode(hsv_mask_m,kernel,iterations = 3)	
	
	moji_y = cv2.warpPerspective(img_y, M,(100,100))
	moji_c = cv2.warpPerspective(img_c, M,(100,100))
	moji_m = cv2.warpPerspective(img_m, M,(100,100))

	moji90_y = cv2.rotate(moji_y, cv2.ROTATE_90_CLOCKWISE)
	moji90_m = cv2.rotate(moji_m, cv2.ROTATE_90_CLOCKWISE)
	moji90_c = cv2.rotate(moji_c, cv2.ROTATE_90_CLOCKWISE)


	moji_y_2 = cv2.warpPerspective(img_y, M,(50,90))
	moji_c_2 = cv2.warpPerspective(img_c, M,(50,90))
	moji_m_2 = cv2.warpPerspective(img_m, M,(50,90))

	moji90_y2 = cv2.rotate(moji_y_2, cv2.ROTATE_90_CLOCKWISE)
	moji90_m2 = cv2.rotate(moji_m_2, cv2.ROTATE_90_CLOCKWISE)
	moji90_c2 = cv2.rotate(moji_c_2, cv2.ROTATE_90_CLOCKWISE)

	img = cv2.cvtColor(orig, cv2.COLOR_BGR2GRAY)
        ret, img = cv2.threshold(img, 100, 255, cv2.THRESH_BINARY)
        img = cv2.erode(img,kernel,iterations = 3)
        moji = cv2.warpPerspective(img, M,(100,100))
        moji90 = cv2.rotate(moji, cv2.ROTATE_90_CLOCKWISE)
        #moji90 =mojiz
        pil_img = Image.fromarray(moji90)
	
	pil_img_y = Image.fromarray(moji90_y)
	pil_img_m = Image.fromarray(moji90_m)
	pil_img_c = Image.fromarray(moji90_c)

	pil_img_y2 = Image.fromarray(moji90_y2)
	pil_img_m2 = Image.fromarray(moji90_m2)
	pil_img_c2 = Image.fromarray(moji90_c2)	

	whole_area_y=moji_y_2.size
 	whole_area_m=moji_m_2.size
 	whole_area_c=moji_c_2.size
 	white_area_y=cv2.countNonZero(moji_y_2)
 	white_area_m=cv2.countNonZero(moji_m_2)
 	white_area_c=cv2.countNonZero(moji_c_2)

	builder = pyocr.builders.TextBuilder(tesseract_layout=5)
	result = tool.image_to_string(pil_img, lang="eng", builder=builder)

        if 'c' in result:
            result = 'C'
        elif 'C' in result:
            result = 'C'
        elif 'E' in result:
            result = 'B'
        elif 'B' in result:
            result = 'B'
        else:
            result = 'A'

	print(result)


	if white_area_y > 1800 and white_area_y < 2100:
		print('R_Yellow_A')
		b=2
	if white_area_y > 1000 and white_area_y < 1750:
		print('R_Yellow_B')
		b=5
	if white_area_y > 2250:
		print('R_Yellow_C')
		b=8

	if white_area_m > 1800 and white_area_m < 2100:
		print('R_Magenta_A')
		b=1
	if white_area_m > 1000 and white_area_m < 1750:
		print('R_Magenta_B')
		b=4
	if white_area_m > 2250:
		print('R_Magenta_C')
		b=7

	if white_area_c > 1800 and white_area_c < 2100:
		print('R_Cyan_A')
		b=0
	if white_area_c > 1000 and white_area_c < 1750:
		print('R_Cyan_B')
		b=3
	if white_area_c > 2250:
		print('R_Cyan_C')
		b=6


        print(white_area_c)


	# if white_area_c > 1800 and white_area_c < 2100:
	# 	print('R_Cyan_A')
	# 	b=0
	# if white_area_c > 1000 and white_area_c < 1500:
	# 	print('R_Cyan_B')
	# 	b=3
	# if white_area_c > 2250:
	# 	print('R_Cyan_C')
	# 	b=6


	pub2.publish(b)

        #cv2.imshow('Y_R', moji_y)
	#cv2.imshow('C_R', moji_c)
	#cv2.imshow('M_R', moji_m)

	#cv2.imshow('Y2', moji_y_2)
	#cv2.imshow('C2', moji_c_2)
	#cv2.imshow('M2', moji_m_2)

	# cv2.imshow('m',hsv_mask_m)
 	# cv2.imshow('y',hsv_mask_y)
 	cv2.imshow('c',hsv_mask_c)
	# cv2.imshow('img',origS)

	#print(white_area_y)
	#print(white_area_c)
	#print(white_area_m)

        #print(result)
        cv2.waitKey(1)
    except Exception as err:
        print err

def start_node():
    rospy.init_node('img_proc_R')
    rospy.loginfo('img_proc node started')
    rospy.Subscriber("/camera/color/image_raw/compressed", CompressedImage, process_image)
    rospy.spin()

if __name__ == '__main__':
    try:
        start_node()
    except rospy.ROSInterruptException:
        pass

