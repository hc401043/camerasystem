import cv2
import numpy as np
from imageExtraction import ImageExtraction

class HueImageExtraction(ImageExtraction):
    def __init__(self,panel,imgprocess):
        super(HueImageExtraction,self).__init__(panel,imgprocess)

    def start(self):
        self.imgprocess.start()
        self.clipImage()
        self.hsvchannel = self.imgprocess.getResultHsvImage()
        if self.hsvchannel is None:
            return

        #self.hsvchannel = self.getResultHsvImage()

        self.g_mask = np.zeros(self.hsvchannel[0].shape, dtype=np.uint8)
        st,ed = self.svpanel.getGreenRange()
        self.g_mask[( (self.hsvchannel[0] >st/2 ) &  (self.hsvchannel[0] < ed/2) )& ((self.hsvchannel[1] > 40) & (self.hsvchannel[2] > 64))] = 255
        # green だけ、黒線のエッジが影響するのでローパスフィルタで処理
        self.g_mask = cv2.blur(self.g_mask,(3,3))
        _, self.g_mask = cv2.threshold(self.g_mask,200,255,cv2.THRESH_BINARY)


        self.r_mask = np.zeros(self.hsvchannel[0].shape, dtype=np.uint8)
        st,ed = self.svpanel.getRedRange()
        if(st<ed):
            self.r_mask[( (self.hsvchannel[0] >st/2 ) &  (self.hsvchannel[0] < ed/2) )& ((self.hsvchannel[1] > 40) & (self.hsvchannel[2] > 64))] = 255
        else:
            self.r_mask[(((self.hsvchannel[0] >= 0) &  (self.hsvchannel[0] < ed/2)) |\
            ((self.hsvchannel[0] >st/2 ) &  (self.hsvchannel[0] <= 180))) &  ((self.hsvchannel[1] > 40) & (self.hsvchannel[2] > 64))] = 255

        self.b_mask = np.zeros(self.hsvchannel[0].shape, dtype=np.uint8)
        st,ed = self.svpanel.getBlueRange()
        self.b_mask[((self.hsvchannel[0] >st/2) &  (self.hsvchannel[0] < ed/2)) &  ((self.hsvchannel[1] > 40) & (self.hsvchannel[2] > 64) )] = 255

        self.y_mask = np.zeros(self.hsvchannel[0].shape, dtype=np.uint8)
        st,ed = self.svpanel.getYellowRange()
        self.y_mask[((self.hsvchannel[0] >st/2 ) &  (self.hsvchannel[0] < ed/2)) &  ((self.hsvchannel[1] > 40) & (self.hsvchannel[2] > 64) )] = 255

        self.bk_mask = np.zeros(self.hsvchannel[0].shape, dtype=np.uint8) 

        #bk_mask = np.full(self.hsvchannel[0].shape, 255, dtype=np.uint8) 
        bv,bs = self.svpanel.getBlackVS()
        # print(bv,bs)
        self.bk_mask[ (self.hsvchannel[1] <= bs) & (self.hsvchannel[2] <= bv)] = 255
        back_mask_img  = self.getClipMaskImage()
        one, _ , _ = cv2.split(back_mask_img)

        self.morpholgy()
    
        self.r_mask = cv2.bitwise_and(self.r_mask,one)
        self.g_mask = cv2.bitwise_and(self.g_mask,one)
        self.b_mask = cv2.bitwise_and(self.b_mask,one)
        self.y_mask = cv2.bitwise_and(self.y_mask,one)
        self.bk_mask = cv2.bitwise_and(self.bk_mask,one)
        #cv2.imshow("g_mask2", g_mask)  


        self.mask = cv2.bitwise_or(self.b_mask,self.g_mask)
        self.mask = cv2.bitwise_or(self.mask,self.r_mask)
        self.mask = cv2.bitwise_or(self.mask,self.y_mask)
        self.mask = cv2.bitwise_or(self.mask,self.bk_mask)

        #cv2.imshow("bk_mask", bk_mask)
        
        self.masks = (self.r_mask,self.g_mask,self.b_mask,self.y_mask,self.bk_mask)

        h_s = self.hsvchannel[1]*(self.mask/255.0) # mask以外のS値を0に
        h_s = h_s.astype('uint8')
        
        #newimg = cv2.merge((self.hsvchannel[0], h_s, self.hsvchannel[2]))
        #self.resultImage = cv2.cvtColor(newimg, cv2.COLOR_HSV2BGR)

        self.resultImage = cv2.merge((self.r_mask,self.g_mask,self.b_mask,self.y_mask,self.bk_mask))

        self.view_thum()

    def morpholgy(self):
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
        itr = 4
        self.g_mask = cv2.dilate(self.g_mask,kernel,iterations = itr+3)
        self.g_mask = cv2.erode(self.g_mask,kernel,iterations = itr+3)
        self.b_mask = cv2.dilate(self.b_mask,kernel,iterations = itr)
        self.b_mask = cv2.erode(self.b_mask,kernel,iterations = itr)
        self.r_mask = cv2.dilate(self.r_mask,kernel,iterations = itr)
        self.r_mask = cv2.erode(self.r_mask,kernel,iterations = itr)
        self.bk_mask = cv2.dilate(self.bk_mask,kernel,iterations = itr)
        self.bk_mask = cv2.erode(self.bk_mask,kernel,iterations = itr)

    def view_thum(self):
        self.imshow_scale("g_mask", self.g_mask,0.25)
        self.imshow_scale("r_mask", self.r_mask,0.25)
        self.imshow_scale("b_mask", self.b_mask,0.25)
        self.imshow_scale("y_mask", self.y_mask,0.25)
        self.imshow_scale("bk_mask", self.bk_mask,0.25)


    def imshow_scale(self,name,img,scale):
        scale_img = cv2.resize(img,(int(img.shape[1]*scale),int(img.shape[0]*scale)))
        cv2.imshow(name,scale_img)
