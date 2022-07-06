import cv2
import numpy as np
import threading as th
import tkinter as tk
import serial as sr
import time
import sys
import math
import os
import copy

from bluetooth import Bluetooth
from svpanel import SV_Panel
from setting import Setting
#from ai.ainumber import AiNumber

from imageContrast import ImageContrast
from hueImageExtraction import HueImageExtraction
from contourImageExtraction import ContourImageExtraction
from subtractImageExtraction import SubtractImageExtraction
from origineImage import OrigineImage
from imageExtractionContrast import ImageExtractionContrast

from capture import Capture


class ET2019Main:
    def __init__(self):
 #       self.maskpt =  [[0,0], [0,720], [1280, 720], [1280,0]]
        self.debug = False
        ## デバッグ用ファイル名設定
       # self.input_img_fname = "L2019/Hno_block.jpg"
       # self.next_input_img_fname = "L2019/Hnum6.jpg"
        #self.input_img_fname = "capture/honbanR/capt7base.jpg"
        #self.next_input_img_fname = "capture/honbanR/capt13after.jpg"
        self.input_img_fname = "capture/honbanL/capt2base.jpg"
        self.next_input_img_fname = "capture/honbanL/capt10after.jpg"

        self.bt = Bluetooth("COM41",9600)

        self.drag = -1  
        self.pickup_mode = 'none'
        self.root = tk.Tk()
        self.root.title(u"メインメニュー")
        self.root.geometry("300x300")
        btn1 = tk.Button(text="映像取得開始",command=self.start_thread)
        btn1.pack()

        btn2 = tk.Button(text="キャリブレーション完了",command=self.finish_carib)
        btn2.pack()

        self.bln = tk.BooleanVar()
        self.bln.set(False)
        chk = tk.Checkbutton(variable=self.bln, text="debug用基準画像(base_img.jpeg)を使用")
        chk.pack()


        btn3 = tk.Button(text="結果送信開始",command=self.start_bt_thread)
        btn3.pack()
        btn4 = tk.Button(text="送信ポートクローズ",command=self.close_bt_port)
        btn4.pack()


        self.ent = tk.Entry(width=40)
        self.ent.pack()

        self.lbl1txt = tk.StringVar()
        self.lbl1txt.set("キャリブレーション中")
        self.lbl1 = tk.Label(textvariable = self.lbl1txt )
        self.lbl1.pack()
        self.lbl2txt = tk.StringVar()
        self.lbl2txt.set("送信停止中")

        self.lbl2 = tk.Label(textvariable = self.lbl2txt)
        self.lbl2.pack()

        self.capture = Capture()
        capt = tk.Button(text="キャプチャ",command=self.exec_capt)
        capt.pack() 

        try:
            setfile = sys.argv[1]
        except IndexError:
            setfile = "default.txt"

        self.svpanel = SV_Panel(self,setfile)
        self.svpanel.makePanel()

        self.nodes = []
        self.carib = True
        self.block_detection=False

        self.block = [0]*25

        self.block_circle_start_num = [[0,10,2,8], # Lコース交点ブロック色別開始番号
                                        [2,8,0,10]] # Rコース
        #self.ainum = AiNumber()
        #self.ainum.course = self.svpanel.setting.course
        self.isconnect=False
        self.finish_process=False

    def exec_capt(self):
        self.capture.capt(self.cap_img)
        

    # マウスイベント時に処理を行う
    def mouse_event(self,event, x, y, flags, param):
        if self.pickup_mode=="none":
            if event==cv2.EVENT_LBUTTONUP:
                self.drag = -1

            if event==cv2.EVENT_LBUTTONDOWN:
                for i,pt in enumerate(self.svpanel.setting.maskpt):
                    if np.linalg.norm(np.array(pt)-np.array([x*2,y*2]))<16:
                        self.drag = i
                        break
                for i,pt in enumerate(self.svpanel.setting.nummaskpt):
                    if np.linalg.norm(np.array(pt)-np.array([x*2,y*2]))<16:
                        self.drag = i+4
                        break
                

            if 0<=self.drag<=3 and event==cv2.EVENT_MOUSEMOVE:
                self.svpanel.setting.maskpt[self.drag]= [x*2,y*2]
            if 4<=self.drag<=5 and event==cv2.EVENT_MOUSEMOVE:
                self.svpanel.setting.nummaskpt[self.drag-4]= [x*2,y*2]
            
                
        elif self.pickup_mode=="red":
            if event==cv2.EVENT_LBUTTONUP:
                print ("red pickup")
                print(self.hsvchannel[0][y*2][x*2]*2)
                self.svpanel.set_red_h(self.hsvchannel[0][y*2][x*2]*2)
                self.pickup_mode="none"
        elif self.pickup_mode=="green":
            if event==cv2.EVENT_LBUTTONUP:
                print ("green pickup")
                self.svpanel.set_green_h(self.hsvchannel[0][y*2][x*2]*2)
                self.pickup_mode="none"
        elif self.pickup_mode=="blue":
            if event==cv2.EVENT_LBUTTONUP:
                print ("blue pickup")
                self.svpanel.set_blue_h(self.hsvchannel[0][y*2][x*2]*2)
                self.pickup_mode="none"
        elif self.pickup_mode=="yellow":
            if event==cv2.EVENT_LBUTTONUP:
                print ("yellow pickup")
                self.svpanel.set_yellow_h(self.hsvchannel[0][y*2][x*2]*2)
                self.pickup_mode="none"
    def finish_carib(self):
        fname = "base_img.jpeg"
        if self.bln.get() and os.path.exists(fname):
            print("＊＊＊保存ベース画像を使用します＊＊＊")
            self.base_img = cv2.imread(fname)
        else:
            self.base_img = self.backup_img.copy()
            cv2.imwrite(fname, self.base_img)

        self.cross_rects = copy.deepcopy(self.contour.viewrects)

        #self.finish_process = True

        #self.subtract = SubtractImageExtraction(self.svpanel,self.contrastImage)
        
        #self.subtract.setBaseImage(self.contrastImage.getResultRgbImage())
        self.subtract.setBaseImage(self.origineImage.getResultRgbImage())
   
        #self.segment = HueImageExtraction(self.svpanel,self.subtract)
        #self.contour = ContourImageExtraction(self.svpanel,self.segment)
        #self.segment.imgprocess = self.subtract #org
        self.contrastImage.imgprocess = self.subtract
        #self.subtract.setInputImage(self.org_frame)

        #self.finish_process = False

        self.input_img_fname = self.next_input_img_fname

        self.carib = False
        self.bt.debug_str = ""
        self.start_bt_thread()
        self.lbl1txt.set("キャリブレーション完了")

    def imshow_scale(self,name,img,scale):
        scale_img = cv2.resize(img,(int(img.shape[1]*scale),int(img.shape[0]*scale)))
        cv2.imshow(name,scale_img)

    def inset_rect(self,r1,r2):
        xmn1 = r1[0]
        ymn1 = r1[1]+r1[3]
        xmx1 = r1[0]+r1[2]
        ymx1 = r1[1]

        xmn2 = r2[0]
        ymn2 = r2[1]+r2[3]
        xmx2 = r2[0]+r2[2]
        ymx2 = r2[1]
       # return (xmn2 <= xmx1 <= xmx2 and ymx2 <= ymx1 <=ymn2) or (xmn2 <= xmn1 <= xmx2 and ymx2 <= ymn1 <=ymn2)
        return max(r1[0],r2[0])<=min(r1[0]+r1[2],r2[0]+r2[2]) and max(r1[1],r2[1])<=min(r1[1]+r1[3],r2[1]+r2[3])
    def point_in_poly(self, pt, polypt):
        if len(pt)<1:
            return False
        if len(polypt)<3:
            return False

        v1 = polypt[0][0]-pt[0], polypt[0][1]-pt[1]
        v2 = polypt[1][0]-pt[0], polypt[1][1]-pt[1]
        v3 = polypt[3][0]-pt[0], polypt[3][1]-pt[1]
        v4 = polypt[2][0]-pt[0], polypt[2][1]-pt[1]
        angle = self.radian_vector(v1,v2)
        #print (angle)
        angle = angle + self.radian_vector(v2,v3)
        #print (angle)
        angle = angle + self.radian_vector(v3,v4)
        #print (angle)
        angle = angle + self.radian_vector(v4,v1)
       # print (math.degrees(angle))
        return abs(math.degrees(angle)-360)<1.0

    def inner_product(self, v1,v2):
        return v1[0]*v2[0]+v1[1]*v2[1]
    def length_vector(self,v):
        return math.sqrt(v[0]*v[0]+v[1]*v[1])
    def radian_vector(self,v1,v2):
        try:
            return math.acos(self.inner_product(v1,v2)/(self.length_vector(v1)*self.length_vector(v2)))
        except Exception:
            print("zero divide error")

        return 0

    # カメラ映像入力スレッド用
    def camera_input(self):
        while True:
            if not self.debug:
                fname = "base_img.jpeg"
                if self.carib and self.bln.get() and os.path.exists(fname):
                    self.cap_img = cv2.imread(fname)
                else:
                    ret, self.cap_img = self.cap.read()
                self.old_img = cv2.addWeighted(self.old_img,0.5,self.cap_img,0.5,0)
            else:
                self.old_img = cv2.imread(self.input_img_fname) #デバッグ用静止画像


    def main_th(self):
        global cont

        color_str = ("blue","green","red","yellow","black")
        
        """
        self.contrastImage = ImageContrast(self.svpanel)
        self.origineImage = OrigineImage(self.svpanel)
         
        self.subtract = SubtractImageExtraction(self.svpanel,self.origineImage)
        self.segment = HueImageExtraction(self.svpanel,self.contrastImage)
        self.contour = ContourImageExtraction(self.svpanel,self.segment)
        """
        self.origineImage = OrigineImage(self.svpanel)
        self.subtract = SubtractImageExtraction(self.svpanel,self.origineImage)
        self.contrastImage = ImageExtractionContrast(self.svpanel,self.origineImage)
        self.segment = HueImageExtraction(self.svpanel,self.contrastImage)
        self.contour = ContourImageExtraction(self.svpanel,self.segment)


        while True: 
            if self.old_img is None: continue

            h,w,_ = self.old_img.shape
            self.org_frame = self.old_img.copy()

            self.ainum.area = self.svpanel.setting.nummaskpt
            aitmp = self.org_frame[  self.ainum.area[0][1]:self.ainum.area[1][1], self.ainum.area[0][0]:self.ainum.area[1][0]]
        
            self.ainum.makeAiFrame(aitmp)
            #self.ainum.showAiFrame()
            if self.carib:
                airect = self.ainum.detNumberFrame()
                self.ainum.storeFixedFrame(airect)
            else:
                airect = self.ainum.fixedarea

            if len(airect)!=0:
                numimg = self.ainum.transform(airect)
                self.bt.bonus = self.ainum.guessNumber(numimg)
            

            self.backup_img = self.org_frame.copy()

            if not self.carib:
                #self.org_frame = self.createObjectMask(self.org_frame)
                self.block_detection=True
  
            if self.finish_process:
                continue
            # self.contrastImage.setInputImage(self.org_frame) # org
            self.origineImage.setInputImage(self.org_frame)

            #self.contrastImage.start()
            #back_mask_img = self.contrastImage.getClipMaskImage()


            #self.segment.setInputImage(self.org_frame) # org
            """
            if self.carib:
                self.contrastImage.setInputImage(self.org_frame)
            else:
                self.subtract.setInputImage(self.org_frame)
            """

            #self.subtract.setBaseImage(self.org_frame)
            #self.subtract.start()
            #self.segment.start()
            self.contour.start()
            #masks = self.segment.masks

            self.hsvchannel = self.contrastImage.getResultHsvImage()

            if self.contrastImage.resultImage is not None:
                ui_frame = self.contrastImage.resultImage.copy()
            
                cv2.rectangle(ui_frame,tuple(self.ainum.area[0]), tuple(self.ainum.area[1]), (255,0,0) , 1 )

                ui_frame = cv2.resize(ui_frame,(int(ui_frame.shape[1]/2),int(ui_frame.shape[0]/2)))
                prev_pt = None
                for pt in self.svpanel.setting.maskpt:
                    cv2.circle(ui_frame, center =(int(pt[0]/2),int(pt[1]/2)), radius = 6 , color = (0,0,255), thickness=2)
                    if prev_pt is not None:
                        cv2.line(ui_frame,((int(prev_pt[0]/2),int(prev_pt[1]/2))),((int(pt[0]/2),int(pt[1]/2))), (0,0,255), 2)
                    else :
                        first_pt=pt
                    prev_pt=pt

                cv2.line(ui_frame,((int(prev_pt[0]/2),int(prev_pt[1]/2))),((int(first_pt[0]/2),int(first_pt[1]/2))), (0,0,255), 2)

                for pt in self.svpanel.setting.nummaskpt:
                    cv2.circle(ui_frame, center =(int(pt[0]/2),int(pt[1]/2)), radius = 6 , color = (255,0,0), thickness=2)

                cv2.imshow("UI image", ui_frame)
                cv2.setMouseCallback("UI image", self.mouse_event)

            """
            self.imshow_scale("g_mask", self.segment.g_mask,0.25)
            self.imshow_scale("r_mask", self.segment.r_mask,0.25)
            self.imshow_scale("b_mask", self.segment.b_mask,0.25)
            self.imshow_scale("y_mask", self.segment.y_mask,0.25)
            self.imshow_scale("bk_mask", self.segment.bk_mask,0.25)
            """
            draw_line_col = ((0,0,255),(0,255,0),(255,0,0),(0,255,255),(100,100,100))
            if not self.block_detection:
                self.nodes = []  # キャリブレーション中だけ更新されるので初期化
               # self.contour.viewrects = [] #交点サークルの保存
               # self.cross_rects = copy.deepcopy(self.contour.viewrects)
            else:
                self.contour.blackdetect = True
                # 交点サークルの描画
                for pt,drawrect,color_idx in self.cross_rects:
                    cv2.rectangle(self.backup_img,(drawrect[0],drawrect[1]),(drawrect[0]+drawrect[2],drawrect[1]+drawrect[3]),draw_line_col[color_idx],2)
            cnt = 0

            #色ごとのマスク処理
            self.block = [[],[],[],[],[], [],[],[],[],[], [],[],[],[],[], [],[],[],[],[],  [],[],[],[],[]]
            # ビンゴサークルの色、ビンゴサークルに置かれるブロックの正当性チェック用
            self.bingocircle_col = [[3,1,0,2,3,1,0,2], #Lの色パターン 
                                    [0,1,3,3,2,2,0,1]] #Rの色パターン
            if self.svpanel.setting.course=='L':
                select= 0
            else:
                select =1

            """
            # maskの順番 r g b y bk
            for i, cur_mask in enumerate(masks): 
                if i!=4 : #黒以外
                    contours, hierarchy = cv2.findContours(cur_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                else:
                    contours, hierarchy = cv2.findContours(cur_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)


                c_nodes = []
                c_nodes_rect = []
                # 各色の領域ごとに処理
                for j,contour in enumerate(contours):
                    area = cv2.contourArea(contour,False)
                    rect = cv2.boundingRect(contour)
                    rectarea = rect[2]*rect[3]

                    #大きさ不適合
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
                        c_nodes.append([cx,cy])
                        c_nodes_rect.append(rect)

                    #print (M,cx,cy)
                    #debug
                    if (not self.block_detection) and i!=4: # 黒以外を交点サークルとして rects に登録
                        rects.append(((cx,cy),rect,i))
                        #print(color_str[i],rect)

                    #cv2.drawContours(self.backup_img,[box],0,draw_line_col[i],2)
                    cv2.rectangle(self.backup_img,(rect[0],rect[1]),(rect[0]+rect[2],rect[1]+rect[3]),draw_line_col[i],2)
                    #cv2.circle(self.backup_img, center =(cx,cy), radius = 3 , color= draw_line_col[i], thickness=2)


                    #⃣ブロック識別
                    if self.block_detection:

                        cross=False
                        block_rgn=[]
                        for node_no,node_pt,node_rect in self.nodes:
                            #print ("color",i,node_no,rect, "node_rect",node_rect,self.inset_rect(rect, node_rect))
                            if self.inset_rect(rect, node_rect) and rect[1]<=node_rect[1]:
                                #print("交点ブロック置き場", node_no+1,node_pt,rect,node_rect,color_str[i])
                                self.block[node_no].append((i,rect)) # 色を追加
                                cross=True
                        # ブロックサークル
                        if not cross:
                            #print(rect,color_str[i])
                            for no in range(1,9):
                                if i==self.bingocircle_col[select][no-1] or i==4:   # ブロックとビンゴサークルが同色か黒のみ存在可能
                                    block_circle_rect = self.getBlockCircleRects(no,self.nodes)
                                   # print(("point in poly ",self.point_in_poly((cx,cy), block_circle_rect),(cx,cy),block_circle_rect)) 
                                    #print(block_circle_rect)
                                    if self.point_in_poly((cx,cy), block_circle_rect):
                                        #print("ブロックサークル", no,block_circle_rect)
                                        self.block[no+15].append((i,rect))
            """

            #抽出結果描画
            for _,viewrect,col in self.contour.viewrects:
                cv2.rectangle(self.backup_img,(viewrect[0],viewrect[1]),(viewrect[0]+viewrect[2],viewrect[1]+viewrect[3]),draw_line_col[col],2)

            #交点サークルに番号付与
            if self.svpanel.setting.course=='L':
                select= 0
            else:
                select =1
        
            block_start = self.block_circle_start_num[select]
            for col in range(5):
                c_nodes = [x[1] for x in self.contour.regions if x[0]==col]
                c_nodes_rect = [x[2] for x in self.contour.regions  if x[0]==col]
                if not self.block_detection and col!=4:
                    self.decision_circle_node(block_start[cnt], c_nodes,c_nodes_rect,self.svpanel.setting.maskpt)
                  #  print("番号付きノード",self.nodes)
                    cnt = cnt+1
                #⃣ブロック識別
                if self.block_detection:
                    block_rects = [[x[0],x[1]] for x in self.contour.viewrects if x[2]==col]
                    for center,rect in block_rects:
                        cross=False
                        block_rgn=[]
                        for node_no,node_pt,node_rect in self.nodes:
                            #print ("color",i,node_no,rect, "node_rect",node_rect,self.inset_rect(rect, node_rect))
                            if self.inset_rect(rect, node_rect) and rect[1]<=node_rect[1]:
                                #print("交点ブロック置き場", node_no+1,node_pt,rect,node_rect,color_str[i])
                                self.block[node_no].append((col,rect)) # 色を追加
                                cross=True
                        # ブロックサークル
                        if not cross:
                            #print(rect,color_str[i])
                            for no in range(1,9):
                                if col==self.bingocircle_col[select][no-1] or col==4:   # ブロックとビンゴサークルが同色か黒のみ存在可能
                                    block_circle_rect = self.getBlockCircleRects(no,self.nodes)
                                    # print(("point in poly ",self.point_in_poly((cx,cy), block_circle_rect),(cx,cy),block_circle_rect)) 
                                    #print(block_circle_rect)
                                    if self.point_in_poly(center, block_circle_rect):
                                        #print("ブロックサークル", no,block_circle_rect)
                                        self.block[no+15].append((col,rect))
                

            #print ("before ",self.block)
            # 誤検知ブロックの整理
            if self.block_detection:
                self.crrectBlockRgn(self.block,self.nodes)
                #print("after ",self.block)
            

            self.bt.reset_blockinfo()
            for node_no,block in enumerate(self.block):
                #print(node_no,block)
                if len(block)!=0 and len(block[0])!=0:
                    cx = int(block[0][1][0]+block[0][1][2]/2)
                    cy = int(block[0][1][1]+block[0][1][3]/2)
                    cv2.circle(self.backup_img, center =(cx,cy), radius = 8 , color= draw_line_col[block[0][0]], thickness=4)
                  # print(block[0][0])
                    if block[0][0]==0:
                        self.bt.set_red(node_no+1)
                    if block[0][0]==1:
                        self.bt.set_green(node_no+1)
                    if block[0][0]==2:
                        self.bt.set_blue(node_no+1)
                    if block[0][0]==3:
                        self.bt.set_yellow(node_no+1)
                    if block[0][0]==4:
                        self.bt.set_black(node_no+1)

            #print (self.nodes)
            text_color = ((0,0,255),(0,255,0),(255,0,0),(0,255,255)) # RGBY
            text_back_color = ((0,0,0),(0,0,0),(0,0,0),(0,0,0))
            text_color_conv = [0,0, 2, 2, 0,0, 2,2, 3,3, 1,1, 3,3, 1,1]   # Lコース　交点ブロック色パターン
            text_color_conv2 = [2,2, 0, 0, 2,2, 0,0, 1,1, 3,3, 1,1, 3,3]   # Rコース　交点ブロック色パターン

            # 交点ブロック番号の画面への表示
            ###
            for node_no,node_pt,node_rect in self.nodes:
                #print(node_no,node_pt,node_rect)
                if node_no<=15:
                    draw_pt= (node_pt[0]-10,node_pt[1]+40)
                    if self.svpanel.setting.course=='L':
                        col = text_color_conv[node_no]
                    else:
                         col = text_color_conv2[node_no]
                   
                    cv2.putText(self.backup_img,str(node_no+1), draw_pt, cv2.FONT_HERSHEY_PLAIN, 2.0,text_back_color[col],5,cv2.LINE_AA)
                    cv2.putText(self.backup_img,str(node_no+1), draw_pt, cv2.FONT_HERSHEY_PLAIN, 2.0,text_color[col],2,cv2.LINE_AA)
                   # cv2.rectangle(drawimg, [box],draw_line_col[i], 2,6)  
            ###
            #cv2.imshow("h_s", h_s)

            #draw_half_image = cv2.resize(drawimg,(int(drawimg.shape[1]/2),int(drawimg.shape[0]/2)))
            #cv2.imshow("result image", draw_half_image)

            self.imshow_scale("result image",self.backup_img,0.5)

            k = cv2.waitKey(10)
            if k == ord('q'):
                camera_on = False
                break
    """
    　２点(pt1,pt2)を通る直線とptの距離を返す
    """        
    def liner_eq(self,pt1,pt2, pt):
        return abs((pt[1]-pt1[1])*(pt2[0]-pt1[0])-(pt2[1]-pt1[1])*(pt[0]-pt1[0]))/math.sqrt((pt2[1]-pt1[1])*(pt2[1]-pt1[1])+(pt2[0]-pt1[0])*(pt2[0]-pt1[0]))

    """
        offset: 同一色交点ノードの先頭番号
        nodes: 同一色交点ノードのリスト
        frame: 外枠の座標のリスト（左上座標から時計回り）
        nodes に番号付きリストを出力
    """
    def decision_circle_node(self, offset, nodes,rect, frame):
        #print("同一色",nodes,rect,frame)
        x_list = []
        for idx,node in enumerate(nodes):
            len1 = self.liner_eq(frame[0],frame[3],node)
            len2 = self.liner_eq(frame[0],frame[1],node)
            x_list.append((node,(len1,len2),rect[idx]))
        #print(x_list)

        y_sortedlist = sorted(x_list,key=lambda x:(x[1][0])) 
        x_sortedlist = sorted(x_list,key=lambda x:(x[1][1])) 
        #print(x_sortedlist)
        #print(y_sortedlist)
        try:
            x_group = [x_sortedlist[0][0],x_sortedlist[1][0]]
            y_group = [y_sortedlist[0][0],y_sortedlist[1][0]]
            #print(x_group)
            #print(y_group)
        
            for idx, node in enumerate(nodes):
                if node in x_group and node in y_group : # どちらの直線にも近い
                    self.nodes.append((offset,node,rect[idx]))
                if node in x_group and not node in y_group: # X方向にだけ近い
                    self.nodes.append((offset+1,node,rect[idx]))
                if not node in x_group and node in y_group: # Y方向にだけ近い
                    self.nodes.append((offset+4,node,rect[idx]))
                if not node in x_group and not node in y_group: # どちらからも遠い
                    self.nodes.append((offset+5,node,rect[idx]))

        except IndexError:
            print("ノード不足")

    def createObjectMask(self, new_img):
        """
        org_frame_gray = cv2.cvtColor(self.base_img, cv2.COLOR_BGR2GRAY)
        new_frame_gray = cv2.cvtColor(new_img, cv2.COLOR_BGR2GRAY)
        cv2.imshow("org",org_frame_gray)
        cv2.imshow("new",new_frame_gray)
        """
        org_frame = cv2.split(self.base_img)
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
        #cv2.imshow("erode",fgmask_all)

        fgmask_all_not = cv2.bitwise_not(fgmask_all)
        fgmask_not_frame = cv2.cvtColor(fgmask_all_not, cv2.COLOR_GRAY2BGR)

      #  fgmask = cv2.morphologyEx(fgmask,cv2.MORPH_CLOSE,kernel)
       # cv2.imshow("mask",fgmask)

        mask_img = cv2.bitwise_and(new_img,new_img,mask=fgmask_all)
        mask_img = cv2.bitwise_or(mask_img,fgmask_not_frame)  # 黒ブロック検出のため背景は白にする。
#        cv2.imshow("mask img",mask_img)
        return mask_img

    def getBlockCircleRects(self,no,rects):
        circleNode = [[0,1,4,5],[1,2,5,6],[2,3,6,7],[4,5,8,9],[6,7,10,11], [8,9,12,13],[9,10,13,14],[10,11,14,15]]
        ret = []
        
        """
        for num,center,rect in rects:
            if num in circleNode[no-1]:
                ret.append(center)
        """
        for c_idx in circleNode[no-1]:
            for num,center,rect in rects:
                if c_idx == num:
                   ret.append(center)
        return ret

    def intersectArea(self,r1,r2):
        sx = max(r1[0],r2[0])
        sy = max(r1[1],r2[1])
        ex = min(r1[0]+r1[2],r2[0]+r2[2])
        ey = min(r1[1]+r1[3],r2[1]+r2[3])

        w = ex-sx
        h = ey-sy

        if w>0 and h>0:
            return w*h
        else:
            return 0

    """
    　認識した１つのブロックが複数領域になってしまった場合に統合する
    """
    def mergeBlockRgn(self,blocks):
        prev_col=-1
        ret = []
        ret_idx=0
        for col,block_rect in blocks:
            if prev_col==col:
                ret[ret_idx][0] = min(ret[ret_idx][0],block_rect[0])
                ret[ret_idx][1] = min(ret[ret_idx][1],block_rect[1])
                ret[ret_idx][2] = max(ret[ret_idx][0]+ret[ret_idx][2],block_rect[0]+block_rect[2])
                ret[ret_idx][3] = max(ret[ret_idx][1]+ret[ret_idx][3],block_rect[1]+block_rect[3])
            else:
                ret.append([col,block_rect])
        return ret


    """
    　影を誤認識した場合にそれを取り除く
      　交点ブロック置き場から外れた面積が大きいものが正しいものとする。
        ブロックサークル置き場にあるものは、最大の面積が正しいものとする。
    """        
    def crrectBlockRgn(self,blocks,circle_rgns):
        for block in blocks:
            block = self.mergeBlockRgn(block)
        for idx,block_rgns in enumerate(blocks):
            # 交点サークルから検索
            cross=False
            for no,_,circle_rgn in circle_rgns:
                #print(no,circle_rgn)
               # print(no,idx,block_rgns)

                if no==idx:
                    area_idx=0
                    area_max=0
                    max_rgns=[]
                    for col,block_rgn in block_rgns:
                        cross=True

                        area = self.intersectArea(block_rgn,circle_rgn)
                        area = block_rgn[2]*block_rgn[3]-area
                        #print ("面積",area)
                        if area_max<area:
                            area_max= area
                            area_max_idx = area_idx
                            max_rgns = col,block_rgn
                        area_idx = area_idx+1
                        
                    blocks[idx] = [max_rgns]
            #ブロックサークル置き場から検索
            if not cross:
                area_idx=0
                area_max=0
                max_rgns=[]
                for col,block_rgn in block_rgns:
                    area = block_rgn[2]*block_rgn[3]
                    if area_max<area:
                        area_max= area
                        area_max_idx = area_idx
                        max_rgns = col,block_rgn
                    area_idx = area_idx+1
                blocks[idx] = [max_rgns]

    def start_thread(self):
        #キャプチャー準備
        if not self.debug:
            self.cap = cv2.VideoCapture('http://192.168.11.100/?action=stream')
            ret, self.old_img = self.cap.read()
        else:
            self.old_img = cv2.imread(self.input_img_fname) #デバッグ用静止画像

        camera_th = th.Thread(target=etmain.camera_input)
        camera_th.setDaemon(True)
        camera_th.start()

        main_th = th.Thread(target=etmain.main_th)
        main_th.setDaemon(True)
        main_th.start()

    def start_bt_thread(self):
        if self.isconnect==False:
            ret = self.bt.open_comport()
            if ret==True:
                print("open完了")
                self.bt.start_send_thread()
                self.isconnect = True
                self.lbl2txt.set("送信中")

                #bt_th = th.Thread(target=bluetooth.send_thread())
                #bt_th.start()
        if self.carib:
            value = self.ent.get()
            value = value.replace('\\n','\n')
            self.bt.debug_str = value

    def close_bt_port(self):
        if self.isconnect:
            self.bt.close_comport()
            self.isconnect = False
            self.bt.stop_send_thread()
            self.lbl2txt.set("送信停止中")


etmain = ET2019Main()
etmain.root.mainloop()

