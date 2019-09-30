import cv2
import numpy as np
from imageExtraction import ImageExtraction

class ContourImageExtraction(ImageExtraction):
    def __init__(self,panel,imgprocess):
        super(ContourImageExtraction,self).__init__(panel,imgprocess)
        self.blackdetect = False
        self.viewrects = []
        self.regions = []

    def start(self):
        self.imgprocess.start()
        masks = cv2.split(self.imgprocess.resultImage)
        self.regions = []
        self.viewrects = []

        for i, cur_mask in enumerate(masks): 
            if i!=4 : #黒以外
                contours, hierarchy = cv2.findContours(cur_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            else:
                contours, hierarchy = cv2.findContours(cur_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

           # self.c_nodes = []
           # self.c_nodes_rect = []
            # 各色の領域ごとに処理
            for j,contour in enumerate(contours):
                area = cv2.contourArea(contour,False)
                rect = cv2.boundingRect(contour)
                rectarea = rect[2]*rect[3]

                #大きさ不適合
                """
                if rect[1]<200 and (rectarea<400 or rectarea>4000) : # 画面上方の場合
                    continue
                if 200<=rect[1]<400 and (rectarea<1000 or rectarea>12000) : # 画面中段の場合
                    continue
                if rect[1]>=400 and (rectarea<2000 or rectarea>22000) : # 画面下方の場合
                    continue
                """
                btm = rect[1]+rect[3]
                if btm<220 and (rectarea<380 or rectarea>4000) : # 画面上方の場合
                    continue
                if 220<=btm<430 and (rectarea<1000 or rectarea>9000) : # 画面中段の場合 R 9500 
                    continue
                if btm>=430 and (rectarea<2000 or rectarea>24000) : # 画面下方の場合
                    continue
                
                #approx = cv2.convexHull(contour)
                minrect = cv2.minAreaRect(contour)
                #debug
                if minrect[1][0]<10 or minrect[1][1]<10:  # 黒線のようなもの
                    continue
                box = cv2.boxPoints(minrect)
                box = np.int0(box)

                M = cv2.moments(contour)
                if M['m00']!=0:
                    cx = int(M['m10']/M['m00'])
                    cy = int(M['m01']/M['m00'])
                    #  c_nodes.append([cx,cy])
                    # c_nodes_rect.append(rect)
                    self.regions.append([i,[cx,cy],rect]) # 色番号、中心座標、矩形

                if self.blackdetect or i!=4: # 黒以外を交点サークルとして rects に登録
                    self.viewrects.append(((cx,cy),rect,i))
                    #print(color_str[i],rect)



