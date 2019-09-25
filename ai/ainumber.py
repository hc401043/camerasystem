import numpy as np
import cv2
import ai.deep_lerning as dl
import threading as th
import time

class AiNumber:
    def __init__(self):
        self.area = [[0,340],[500,720]]
        self.fixedarea = [[],[],[],[]]
        self.img_padding = 50,50
        self.course='L'
        self.running = False
    def setFrame(self,frame):
        self.input=frame

    def makeAiFrame(self,frame):
        h,w,_ = frame.shape
        
        self.bigframe = np.full((h+self.img_padding[1]*2,w+self.img_padding[0]*2,3),255,dtype=np.uint8)
        self.bigframe = cv2.rectangle(self.bigframe,(0,0),(w+self.img_padding[0]*2,h+self.img_padding[1]*2),(0,100,0),-1)
        self.bigframe_white = np.full((h+self.img_padding[1]*2,w+self.img_padding[0]*2,3),255,dtype=np.uint8)

        self.bigframe[self.img_padding[1]:self.img_padding[1]+h,self.img_padding[0]:self.img_padding[0]+w] = frame
        self.bigframe_white[self.img_padding[1]:self.img_padding[1]+h,self.img_padding[0]:self.img_padding[0]+w] = frame
       

    def showAiFrame(self):
        cv2.imshow("ainumber",self.bigframe)
    
    def detNumberFrame(self):
        num_rect=[[0,0],[100,0],[100,100],[0,100]]

        #矩形自動抽出
        clip_hsv = cv2.cvtColor(self.bigframe, cv2.COLOR_BGR2HSV)

        # 緑のフレームを抽出処理
        hsvLower = np.array([80/2, 60, 0])    # 抽出する色の下限(HSV)
        hsvUpper = np.array([170/2, 255, 200])    # 抽出する色の上限(HSV)

        h_mask = cv2.inRange(clip_hsv, hsvLower, hsvUpper)
        cv2.imshow("hmask",h_mask)
        #モルフォルジ処理
        #kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2,2))
        #h_mask = cv2.erode(h_mask,kernel,iterations = 5)
        #h_mask = cv2.dilate(h_mask,kernel,iterations = 5)

        #ret,thresh = cv2.threshold(clip_gray,127,255,0)
        num_rect=[[0,0],[100,0],[100,100],[0,100]]
        contours,hierarchy = cv2.findContours(h_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        #cv2.drawContours(cliped, contours, -1, (0, 255, 0), 3)
        #cv2.imshow('cliped',cliped)

        # ２階層目のcontoursの中で面積が規定以上
        for i in range(len(contours)):
            if hierarchy[0][i][3]!=-1:
                if cv2.contourArea(contours[i])>25000:
                    cv2.drawContours(self.bigframe, contours, i, (0, 255, 0), 3)
                    #epsilon = 0.02*cv2.arcLength(contours[i],True)
                    epsilon=20
                    approx = cv2.approxPolyDP(contours[i],epsilon,True)
                    hull = cv2.convexHull(approx,returnPoints = True)
                    #im = cv2.polylines(cliped,[approx],True,(0,0,255),2)
                    #左端にあるものが数字カード置き場
                    find = False
                    for j in range(len(hull)):
                        if self.course=='L' and hull[j][0][0]<150:
                            find=True
                        if self.course=='R' and hull[j][0][0]>self.bigframe.shape[1]-150:
                            find=True

                    if find:
                        #print(hull)
                        cv2.drawContours(self.bigframe, [hull], -1, (0, 0, 255), 2)

                        num_rect = self.guessNumberRect(hull,self.course)
                        #print(self.course,num_rect)

            #im = cv2.drawContours(cliped,[box],0,(0,0,255),2)
            #im = cv2.drawContours(cliped,hulls,0,(0,0,255),2)

                    #print(approx)

                    cv2.imshow('cliped',self.bigframe)
        return num_rect
    def storeFixedFrame(self,num_rect):
        self.fixedarea = num_rect

    # 透視変換で数字を正体化
    def transform(self,num_rect):
        minx,miny = 0,0
        # 出力座標の計算(三平方の定理)
        r_btm = list(map(lambda x,y: x+y, num_rect[2], [minx,miny]))
        r_top = list(map(lambda x,y: x+y, num_rect[1],  [minx,miny]))
        l_top = list(map(lambda x,y: x+y, num_rect[0],  [minx,miny]))
        l_btm = list(map(lambda x,y: x+y, num_rect[3],  [minx,miny]))
       # print([l_top,r_top,r_btm,l_btm])

        #r_btm = nummaskpt[3]   
        #r_top = nummaskpt[1]
        #l_top = nummaskpt[0]
        #l_btm = nummaskpt[2]
        # 長いラインを矩形の辺の長さとしｈて採用
        top_line   = (abs(r_top[0] - l_top[0]) ^ 2) + (abs(r_top[1] - l_top[1]) ^ 2)
        btm_line   = (abs(r_btm[0] - l_btm[0]) ^ 2) + (abs(r_btm[1] - l_btm[1]) ^ 2)
        left_line  = (abs(l_top[0] - l_btm[0]) ^ 2) + (abs(l_top[1] - l_btm[1]) ^ 2)
        right_line = (abs(r_top[0] - r_btm[0]) ^ 2) + (abs(r_top[1] - r_btm[1]) ^ 2)
        max_x = top_line  if top_line  > btm_line   else btm_line
        max_y = left_line if left_line > right_line else right_line

        #結局縦横でも長い方を正方形の長さとして採用
        if max_x<max_y:
                max_x=max_y
        # 異常値のまま先に進むとメモリエラーになるのでここで制限
        if max_x>1000:
            max_x=1000
        #pts1 = np.float32(num_rect)
        pts1 = np.float32([l_top,r_top,r_btm,l_btm])
        pts2 = np.float32([ [100, 0], [max_x-100, 0],[max_x-100, max_x], [100, max_x]])

        #print (pts1,pts2)

        # 透視変換の行列を求める
        M = cv2.getPerspectiveTransform(pts1, pts2)

        # 変換行列を用いて画像の透視変換
        src = self.bigframe_white
        dst = cv2.warpPerspective(src, M, (max_x, max_x),borderValue=(255, 255, 255))

        cv2.rectangle(dst, (0, 0), (110, dst.shape[0]), (255, 255, 255), -1) # 淵を白に消去
        cv2.rectangle(dst, (dst.shape[1]-110, 0), (dst.shape[1], dst.shape[0]), (255, 255, 255), -1) # 淵を白に消去
        cv2.rectangle(dst, (0, 0), (dst.shape[1], 50), (255, 255, 255), -1) # 淵を白に消去
        cv2.rectangle(dst, (0, dst.shape[0]-50), (dst.shape[1], dst.shape[0]), (255, 255, 255), -1) # 淵を白に消去
        # さらに斜めに変換すると６が認識しやすい。MNISTのデータが手書き想定だから？
        """	
        slide = 100
        pts1 = np.float32([[0, 0], [max_x, 0],[0, max_x], [max_x, max_x]])
        pts2 = np.float32([ [0+slide*1.5, 0], [max_x-slide*0.5, 0],[0+slide*1.5, max_x], [max_x-slide*0.5, max_x+0]])
        M = cv2.getPerspectiveTransform(pts1, pts2)
        dst = cv2.warpPerspective(dst, M, (max_x, max_x),borderValue=(255, 255, 255))
        """
        return dst

    def guessNumber(self,src):
        dst = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)

        #数値の閾値処理
        ret, dst = cv2.threshold(dst, 110, 255, cv2.THRESH_BINARY)  #170
        #モルフォルジ処理
        #kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
        #dst = cv2.erode(dst,kernel,iterations = 18)
        #dst = cv2.dilate(dst,kernel,iterations = 20)

        cv2.imshow('result',dst)
        return dl.guess_number(dst)


    #画角から外れた頂点の推測
    def guessNumberRect(self,cont, course):
        #print(cont,len(cont))

        if len(cont)<4:
            return [] 
        # 6点～9点未満であれば点を減らして対応してみる
        while 5<len(cont)<9: 
            newcont = self.reducePoint(cont)
            if len(cont)==len(newcont): #点が減らない場合はそのまま処理継続
                break
            cont = newcont


        if len(cont)!=5:
            return []

        # 上の座標獲得
        min = 10000
        for idx in range(len(cont)):
            if(min>cont[idx][0][1]):
                min = cont[idx][0][1]
                top_idx=idx
        top=cont[top_idx][0]
        if course=='L':
            right = cont[(top_idx+1)%len(cont)][0]
        else:
            left = cont[(top_idx+4)%len(cont)][0]


        # 下の座標獲得
        max = 0
        for idx in range(len(cont)):
            if max<cont[idx][0][1]:
                max = cont[idx][0][1]
                btm_idx=idx
        btm=cont[btm_idx][0]

        term_list=[]
        if course=='L':
            #左の座標を獲得
            for idx in range(len(cont)):
                if cont[idx][0][0]<cont[top_idx][0][0] and cont[idx][0][0]<cont[btm_idx][0][0]:
                    term_list.append(cont[idx][0])
        else:
            #右の座標を獲得
            for idx in range(len(cont)):
                if cont[idx][0][0]>cont[top_idx][0][0] and cont[idx][0][0]>cont[btm_idx][0][0]:
                    term_list.append(cont[idx][0])

        #print(term_list)
        if len(term_list)==0:
            return []

        #左又は右の上下を決定
        if len(term_list)>=2:
            if term_list[0][1]<term_list[1][1]:
                left_up =  term_list[0]
                left_down = term_list[1]
            else:
                left_up =  term_list[1]
                left_down = term_list[0]
        else:
                left_up =  term_list[0]
                left_down = term_list[0]

        a1 = (top[1]-left_up[1])/(top[0]-left_up[0]) # 左上の傾き
        a2 = (btm[1]-left_down[1])/(btm[0]-left_down[0]) # 左下の傾き

        if top[0]-left_up[0]==0:
            print ("error")
            print(top,left_up,left_down)
        if btm[0]-left_down[0]==0:
            print ("error")

        x= int((a1*left_up[0]-a2*left_down[0]-left_up[1]+left_down[1])/(a1-a2))
        y= int(left_up[1]+a1*(x-left_up[0]))
        
        if course=='L':
            ret =  [[x,y],top.tolist(),right.tolist(),btm.tolist()]
        else: 
            ret =  [top.tolist(),[x,y],btm.tolist(),left.tolist()]

        return ret

    #認識の結果が近い２点を１点に統合
    def reducePoint(self,cont):
        num = len(cont)
        min = 100000
        for i in range(num):
            pt1 = cont[i][0]
            pt2 = cont[(i+1)%num][0]
            #print(pt1,pt2)
            length = (pt2[0]-pt1[0])*(pt2[0]-pt1[0]) + (pt2[1]-pt1[1])*(pt2[1]-pt1[1])
            if min>length:
                min = length
                result = i
        
        ret = []
        skip=False
        for i in range(num):
            if skip:
                skip=False
                continue
            if i==result:
                ret.append([np.array([int((cont[i][0][0]+cont[(i+1)%num][0][0])/2),int((cont[i][0][1]+cont[(i+1)%num][0][1])/2)])])	
                skip = True
            else: 
                ret.append([cont[i][0]])
        
        #print(ret)
        return ret

    def aiThread(self):
        while self.running:
            self.makeAiFrame(self.input)
           # self.showAiFrame()
            """
            airect = self.detNumberFrame()
            print(airect)
            if len(airect)!=0:
                numimg = self.transform(airect)
                self.guessNumber(numimg)
            """
           # time.sleep(5)


    def startThread(self,frame):
        if not self.running:
            self.running=True
            self.input = frame
            ai_th = th.Thread(target=self.aiThread)
            ai_th.setDaemon(True)
            ai_th.start()

