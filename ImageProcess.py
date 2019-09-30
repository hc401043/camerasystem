import cv2
import numpy as np
from abc import ABCMeta, abstractmethod

class ImageProcess(metaclass=ABCMeta):
    def __init__(self,panel):
        self.inputImage = None
        self.resultImage = None
        self.svpanel = panel
        #self.clipImage()

    @abstractmethod
    def start(self):
        pass
    
    def clipImage(self):
        size = 720,1280,3 
        # クリップマスクの作成
        self.back_mask_img = np.zeros(size, dtype=np.uint8)
        contours = np.array( self.svpanel.setting.maskpt )
        cv2.fillPoly(self.back_mask_img, pts =[contours], color=(255,255,255)) # クリップ領域内部が255
        #back_not_mask_img = cv2.bitwise_not(self.back_mask_img) #クリップ領域内部が0
        #cv2.imshow("back mask", self.back_mask_img)

        if self.inputImage is not None:
            self.inputImage[self.back_mask_img==0] = [0]

    
    
    def setInputImage(self,img):
        self.inputImage = img.copy()
    
    def getResultRgbImage(self):
        return self.resultImage

    def getResultHsvImage(self):
        if self.resultImage is not None:
            return cv2.split(cv2.cvtColor(self.resultImage, cv2.COLOR_BGR2HSV))
        else: 
            return None

    def getClipMaskImage(self):
        return self.back_mask_img

    
    def rgb2hsv(self):
        self.inputImage = cv2.cvtColor(self.inputImage, cv2.COLOR_BGR2HSV)

    def hsv2rgb(self):
        self.resultImage = cv2.cvtColor(self.resultImage, cv2.COLOR_HSV2BGR)

