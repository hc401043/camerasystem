import cv2
class Capture:
    def __init__(self):
        self.outfilepath = "./capture/"
        self.outfilename = "capt"
        self.captureidx = 0
    
    def capt(self,img):
        cv2.imwrite(self.outfilepath+"/"+self.outfilename+str(self.captureidx)+".jpg", img)
        self.captureidx = self.captureidx+1


