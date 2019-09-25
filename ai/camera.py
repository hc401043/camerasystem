# -*- coding: utf-8 -*-

import cv2
import numpy as np
import deep_lerning as dl
import tkinter as tk
import tkinter.font as font
import threading


first=False

"""
def mouse_event(event, x, y, flags, param):
	global first,st_pt,ed_pt
	if first==False and event==cv2.EVENT_LBUTTONDOWN:
		first = True;
		st_pt = (x , y)
		ed_pt = (x , y)
		print (st_pt)
	
	if first==True and event==cv2.EVENT_MOUSEMOVE:
		ed_pt = (x,y)
	
	if event==cv2.EVENT_LBUTTONUP:
		ed_pt = (x,y)
		first = False
"""

#nummaskpt = [[70,600],[366,400],[364,900],[750,572]]
nummaskpt = [[70,400],[750,900]]
drag= -1
def mouse_event(event, x, y, flags, param):
	global drag
	if event==cv2.EVENT_LBUTTONUP:
		drag = -1

	if event==cv2.EVENT_LBUTTONDOWN:
		for i,pt in enumerate(nummaskpt):
			if np.linalg.norm(np.array(pt)-np.array([x*2,y*2]))<16:
				drag = i
				break

	if drag!=-1 and event==cv2.EVENT_MOUSEMOVE:
		nummaskpt[drag]= [x*2,y*2]


    
def camera_process():
	global st_pt,ed_pt
	#
	
	cap = cv2.VideoCapture('http://192.168.11.100/?action=stream')

	if not cap.isOpened():
		print("カメラオープン失敗")
		exit
	

	cv2.namedWindow("thumbnail", cv2.WINDOW_NORMAL)
	cv2.setMouseCallback('thumbnail', mouse_event)
		
	st_pt=(0,0)
	ed_pt=(0,0)

	while True:
		ret, frame = cap.read()
		#frame = cv2.imread("../R2019/num6.jpg") #デバッグ用静止画像
		h,w,_ = frame.shape

		bigframe = np.full((h+200,w+400,3),255,dtype=np.uint8)
		bigframe = cv2.rectangle(bigframe,(0,0),(w+400,h+200),(0,100,0),-1)
		bigframe_white = np.full((h+200,w+400,3),255,dtype=np.uint8)

		bigframe[100:100+h,200:200+w] = frame
		bigframe_white[100:100+h,200:200+w] = frame

		thum = cv2.resize(bigframe, (int(bigframe.shape[1]/2), int(bigframe.shape[0]/2)))

		global nummaskpt        
		for pt in nummaskpt:		
			cv2.circle(thum, center =(int(pt[0]/2),int(pt[1]/2)), radius = 6 , color = (0,0,255), thickness=2)
		cv2.rectangle(thum,(int(nummaskpt[0][0]/2),int(nummaskpt[0][1]/2)),(int(nummaskpt[1][0]/2),int(nummaskpt[1][1]/2)), (0,0,128),2)

		"""
		minx = min(nummaskpt[0][0],nummaskpt[1][0],nummaskpt[2][0],nummaskpt[3][0])	
		miny = min(nummaskpt[0][1],nummaskpt[1][1],nummaskpt[2][1],nummaskpt[3][1])	
		maxx = max(nummaskpt[0][0],nummaskpt[1][0],nummaskpt[2][0],nummaskpt[3][0])	
		maxy = max(nummaskpt[0][1],nummaskpt[1][1],nummaskpt[2][1],nummaskpt[3][1])	
		"""
		minx = nummaskpt[0][0]
		miny = nummaskpt[0][1]
		maxx = nummaskpt[1][0]
		maxy = nummaskpt[1][1]

		cv2.imshow('thumbnail',thum)
		#cv2.imshow('bigframe',bigframe)

		cliped = bigframe[miny:maxy,minx:maxx]
		clipw = int(cliped.shape[1])
		cliph = int(cliped.shape[0])
		#cliped = np.full((cliph*2,clipw*2,3),255,dtype=np.uint8)
		clipoffset = [int(clipw/2),int(cliph/2)]
		#cliped[clipoffset[1]:clipoffset[1]+cliph,clipoffset[0]:clipoffset[0]+clipw] = cliped_inner


		#矩形自動抽出
		clip_hsv = cv2.cvtColor(cliped, cv2.COLOR_BGR2HSV)

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

		#printprint(len(contours))
		# ２階層目のcontoursの中で面積が規定以上
		for i in range(len(contours)):
			if hierarchy[0][i][3]!=-1:
				if cv2.contourArea(contours[i])>25000:
					cv2.drawContours(cliped, contours, i, (0, 255, 0), 3)
					#epsilon = 0.02*cv2.arcLength(contours[i],True)
					epsilon=20
					approx = cv2.approxPolyDP(contours[i],epsilon,True)
					hull = cv2.convexHull(approx,returnPoints = True)
					#im = cv2.polylines(cliped,[approx],True,(0,0,255),2)
					cv2.drawContours(cliped, [hull], -1, (0, 0, 255), 2)

					num_rect = guessNumberRect(approx,'L')
			#im = cv2.drawContours(cliped,[box],0,(0,0,255),2)
			#im = cv2.drawContours(cliped,hulls,0,(0,0,255),2)

					#print(approx)

					cv2.imshow('cliped',cliped)
		#print(num_rect,len(num_rect))
		if len(num_rect)==0:
			continue

		# 出力座標の計算(三平方の定理)
		r_btm = list(map(lambda x,y: x+y, num_rect[3], [minx,miny]))
		r_top = list(map(lambda x,y: x+y, num_rect[1],  [minx,miny]))
		l_top = list(map(lambda x,y: x+y, num_rect[0],  [minx,miny]))
		l_btm = list(map(lambda x,y: x+y, num_rect[2],  [minx,miny]))

		#r_btm = nummaskpt[3]
		#r_top = nummaskpt[1]
		#l_top = nummaskpt[0]
		#l_btm = nummaskpt[2]
		# 長いラインを矩形の辺の長さとして採用
		top_line   = (abs(r_top[0] - l_top[0]) ^ 2) + (abs(r_top[1] - l_top[1]) ^ 2)
		btm_line   = (abs(r_btm[0] - l_btm[0]) ^ 2) + (abs(r_btm[1] - l_btm[1]) ^ 2)
		left_line  = (abs(l_top[0] - l_btm[0]) ^ 2) + (abs(l_top[1] - l_btm[1]) ^ 2)
		right_line = (abs(r_top[0] - r_btm[0]) ^ 2) + (abs(r_top[1] - r_btm[1]) ^ 2)
		max_x = top_line  if top_line  > btm_line   else btm_line
		max_y = left_line if left_line > right_line else right_line
		#結局縦横でも長い方を正方形の長さとして採用
		if max_x<max_y:
				max_x=max_y
		#pts1 = np.float32(num_rect)
		pts1 = np.float32([l_top,r_top,r_btm,l_btm])
		pts2 = np.float32([ [100, 0], [max_x-100, 0],[100, max_x], [max_x-100, max_x]])

		#print (pts1,pts2)

		# 透視変換の行列を求める
		M = cv2.getPerspectiveTransform(pts1, pts2)

		# 変換行列を用いて画像の透視変換
		src = bigframe_white
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

		#dst = cv2.resize(dst,(int(max_x*0.7),max_x))
		#dst_frame = np.full((max_x, max_x,3),255,dtype=np.uint8)
		#dst_frame[0:max_x,int(max_x*0.15):int(max_x*0.15)+int(max_x*0.7)] = dst


#		print(dst.shape)
		#cv2.rectangle(dst, (0, 0), (dst.shape[1], dst.shape[0]), (255, 255, 255), 80) # 淵を白に消去
		dst = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)

		#数値の閾値処理
		ret, dst = cv2.threshold(dst, 100, 255, cv2.THRESH_BINARY)
		#モルフォルジ処理
		#kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
		#dst = cv2.erode(dst,kernel,iterations = 18)
		#dst = cv2.dilate(dst,kernel,iterations = 20)

		cv2.imshow('result',dst)
		
		global var			
		var.set(dl.guess_number(dst))
			
		## endif	    
		key = cv2.waitKey(1) & 0xFF
		if key == ord("q"):	
			cv2.drawContours(cliped, dict_approx[best_white], -1, (0, 255, 0), 3)
			cv2.imwrite("_detail.{}".format('debug.jpg'), cliped)
			break;

	## end while	

def guessNumberRect(cont, course):
	#print(cont,len(cont))

	if len(cont)<4:
		return []  
	while len(cont)>5:
		cont = reducePoint(cont)


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

	x= int((a1*left_up[0]-a2*left_down[0]-left_up[1]+left_down[1])/(a1-a2))
	y= int(left_up[1]+a1*(x-left_up[0]))
	
	if course=='L':
		ret =  [[x,y],top.tolist(),right.tolist(),btm.tolist()]
	else: 
		ret =  [top.tolist(),[x,y],btm.tolist(),left.tolist()]

	return ret

#近い２点を１点に統合
def reducePoint(cont):
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



th_camera = threading.Thread(target=camera_process, name='camera_body')
th_camera.setDaemon(True)
th_camera.start()

#camera_process()

root = tk.Tk()

my_font_m = font.Font(root,family="System",size=20,weight="bold")
my_font_l = font.Font(root,family="System",size=40,weight="bold")

var = tk.StringVar()
str = tk.Label(text=u'予測した数値', font=my_font_m)
str.pack()
Static1 = tk.Label(textvariable = var, font=my_font_l)
Static1.pack()
tk.mainloop()

