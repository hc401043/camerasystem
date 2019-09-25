import cv2

org_img = cv2.imread('seg_img/img15.jpg')
new_img = cv2.imread('seg_img/img21.jpg')

#org_frame = cv2.split(org_img)
org_frame_gray = cv2.cvtColor(org_img, cv2.COLOR_BGR2GRAY)
#new_frame = cv2.split(new_img)
new_frame_gray = cv2.cvtColor(new_img, cv2.COLOR_BGR2GRAY)
cv2.imshow("org",org_frame_gray)
cv2.imshow("new",new_frame_gray)

kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))

fgbg = cv2.createBackgroundSubtractorMOG2()
fgmask = fgbg.apply(org_frame_gray)
fgmask = fgbg.apply(new_frame_gray)
fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)
ret,fgmask = cv2.threshold(fgmask,30,255,cv2.THRESH_BINARY)
fgmask = cv2.dilate(fgmask,kernel,iterations = 1)

cv2.imshow("mask",fgmask)

mask_img = cv2.bitwise_and(new_img,new_img,mask=fgmask)

cv2.imshow("mask img",mask_img)

#cv2.imshow("org",org_)
"""
diff_frame_b = new_frame[0] - org_frame[0]
diff_frame_g = new_frame[1] - org_frame[1]
diff_frame_r = new_frame[2] - org_frame[2]
"""
#result_img = cv2.merge((diff_frame_b,diff_frame_g,diff_frame_r))
#diff_frame_gray = new_frame_gray - org_frame_gray

#cv2.imshow("result",diff_frame_gray)

cv2.waitKey(0)
