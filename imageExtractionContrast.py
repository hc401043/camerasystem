import cv2
from imageExtraction import ImageExtraction

class ImageExtractionContrast(ImageExtraction):
    def __init__(self,panel,imgprocess):
        super(ImageExtractionContrast,self).__init__(panel,imgprocess)

    def start(self):
        self.imgprocess.start()

        self.inputImage = self.imgprocess.getResultRgbImage()
        self.rgb2hsv()

        #cv2.imshow("cont",self.imgprocess.resultImage)

        self.hsvchannel = cv2.split(self.inputImage)

        self.hsvchannel[1] = cv2.LUT(self.hsvchannel[1], self.svpanel.SLUT)
        self.hsvchannel[2] = cv2.LUT(self.hsvchannel[2], self.svpanel.VLUT)

        self.resultImage = cv2.merge((self.hsvchannel[0],self.hsvchannel[1] ,self.hsvchannel[2])  )
        self.hsv2rgb()


