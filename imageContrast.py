import cv2
from ImageProcess import ImageProcess

class ImageContrast(ImageProcess):
    def __init__(self,panel):
        super(ImageContrast,self).__init__(panel)

    def start(self):
        self.clipImage()
        
        self.rgb2hsv()

        self.hsvchannel = cv2.split(self.inputImage)

        self.hsvchannel[1] = cv2.LUT(self.hsvchannel[1], self.svpanel.SLUT)
        self.hsvchannel[2] = cv2.LUT(self.hsvchannel[2], self.svpanel.VLUT)

        self.resultImage = cv2.merge((self.hsvchannel[0],self.hsvchannel[1] ,self.hsvchannel[2])  )
        self.hsv2rgb()
        
