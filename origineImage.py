import cv2
from ImageProcess import ImageProcess

class OrigineImage(ImageProcess):
    def __init__(self,panel):
        super(OrigineImage,self).__init__(panel)

    def start(self):
        self.clipImage()
        
        self.rgb2hsv()
        self.resultImage = self.inputImage.copy()
        self.hsv2rgb()
        
