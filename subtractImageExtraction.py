import cv2
import numpy as np
from imageExtraction import ImageExtraction

class SubtractImageExtraction(ImageExtraction):
    def __init__(self,panel,imgprocess):
        super(SubtractImageExtraction,self).__init__(panel,imgprocess)
        #self.baseImage = self.imgprocess.inputImage


    def start(self):
        self.imgprocess.start()
        self.resultImage = self.createObjectMask(self.imgprocess.resultImage)

        #cv2.imshow("test1",self.imgprocess.resultImage)
        #cv2.imshow("test2",self.baseImage)


    def setBaseImage(self,img):
        self.baseImage = img.copy()
    
    def createObjectMask(self, new_img):
        org_frame = cv2.split(self.baseImage)
        new_frame = cv2.split(new_img)

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))

        fgbg = [ cv2.createBackgroundSubtractorMOG2(detectShadows = False), \
                 cv2.createBackgroundSubtractorMOG2(detectShadows = False), \
                 cv2.createBackgroundSubtractorMOG2(detectShadows = False) ]

        fgmask = [0]*3
        for i in range(3):
            fgmask[i] = fgbg[i].apply(org_frame[i])
            fgmask[i] = fgbg[i].apply(new_frame[i])
            fgmask[i] = cv2.morphologyEx(fgmask[i], cv2.MORPH_OPEN, kernel)
            ret,fgmask[i] = cv2.threshold(fgmask[i],4,255,cv2.THRESH_BINARY)
        fgmask_all = cv2.bitwise_or(fgmask[0],fgmask[1])
        fgmask_all = cv2.bitwise_or(fgmask_all,fgmask[2])

        fgmask_all = cv2.dilate(fgmask_all,kernel,iterations = 1)
        #cv2.imshow("dilate",fgmask_all)
        fgmask_all = cv2.erode(fgmask_all,kernel,iterations = 4)
       # cv2.imshow("erode",fgmask_all)

        fgmask_all_not = cv2.bitwise_not(fgmask_all)
        fgmask_not_frame = cv2.cvtColor(fgmask_all_not, cv2.COLOR_GRAY2BGR)

      #  fgmask = cv2.morphologyEx(fgmask,cv2.MORPH_CLOSE,kernel)
       # cv2.imshow("mask",fgmask)

        mask_img = cv2.bitwise_and(new_img,new_img,mask=fgmask_all)
        mask_img = cv2.bitwise_or(mask_img,fgmask_not_frame)  # 黒ブロック検出のため背景は白にする。
#        cv2.imshow("mask img",mask_img)
        return mask_img
