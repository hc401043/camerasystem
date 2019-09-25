import cv2
import numpy as np
import threading as th
import tkinter as tk
import serial as sr
import time
from bluetooth import Bluetooth
from svpanel import SV_Panel

"""
def makeGammaLUT(gamma):
	lookUpTable = np.zeros((256, 1), dtype = 'uint8')

	for i in range(256):
	    
	    lookUpTable[i][0] = 255 * pow(float(i) / 255, 1.0 / gamma)
	
	return lookUpTable
"""

def makeSContrastLUT(cont, center):
	tmp = np.zeros((256, 1), dtype = 'float')
	lookUpTable = np.zeros((256, 1), dtype = 'uint8')
	if cont==0: cont=0.001

	for i in range(256):
	    tmp[i][0] = 100 /(1+ np.exp(-cont*(float(i) -center)/100))

	for i in range(256):
		if tmp[255][0]-tmp[0][0]!=0:
			lookUpTable[i][0] = 255*(tmp[i][0]-tmp[0][0])/(tmp[255][0]-tmp[0][0])		
#	print(lookUpTable[0])
	return lookUpTable


def makeGammaLUT(gamma):
	lookUpTableB = np.zeros((256, 1), dtype = 'uint8')
	lookUpTableG = np.zeros((256, 1), dtype = 'uint8')
	lookUpTableR = np.zeros((256, 1), dtype = 'uint8')

	for i in range(256):
	    if gamma[0]==0: gamma[0]=0.001
	    if gamma[1]==0: gamma[1]=0.001
	    if gamma[2]==0: gamma[2]=0.001
	    
	    lookUpTableR[i][0] = 255 * pow(float(i) / 255, 1.0 / gamma[0])
	    lookUpTableG[i][0] = 255 * pow(float(i) / 255, 1.0 / gamma[1])
	    lookUpTableB[i][0] = 255 * pow(float(i) / 255, 1.0 / gamma[2])
	
	lookUpTable = cv2.merge((lookUpTableB,lookUpTableG,lookUpTableR))
	return lookUpTable

def makeBrightLUT(bright):
	lookUpTableB = np.zeros((256, 1), dtype = 'uint8')
	lookUpTableG = np.zeros((256, 1), dtype = 'uint8')
	lookUpTableR = np.zeros((256, 1), dtype = 'uint8')

	for i in range(256):
		if i+bright[0]>255:
			lookUpTableR[i][0] = 255
		elif i+bright[0]<0:
			lookUpTableR[i][0] = 0
		else:
			lookUpTableR[i][0] = i+bright[0] 

		 
		if i+bright[1]>255:
			lookUpTableG[i][0] = 255
		elif i+bright[1]<0:
			lookUpTableG[i][0] = 0
		else:
			lookUpTableG[i][0] = i+bright[1] 

		if i+bright[2]>255:
			lookUpTableB[i][0] = 255
		elif i+bright[2]<0:
			lookUpTableB[i][0] = 0
		else:
			lookUpTableB[i][0] = i+bright[2] 
	
	lookUpTable = cv2.merge((lookUpTableB,lookUpTableG,lookUpTableR))
	return lookUpTable


def makeContrastLUT(cont,center):
	tmpB = np.zeros((256, 1), dtype = 'float')
	tmpG = np.zeros((256, 1), dtype = 'float')
	tmpR = np.zeros((256, 1), dtype = 'float')
	lookUpTableB = np.zeros((256, 1), dtype = 'uint8')
	lookUpTableG = np.zeros((256, 1), dtype = 'uint8')
	lookUpTableR = np.zeros((256, 1), dtype = 'uint8')

	for i in range(256):
	    if cont[0]==0: cont[0]=0.001
	    if cont[1]==0: cont[1]=0.001
	    if cont[2]==0: cont[2]=0.001
	    
	    tmpR[i][0] = 100 /(1+ np.exp(-cont[0]*(float(i) -center[0])/100))
	    tmpG[i][0] = 100 /(1+ np.exp(-cont[1]*(float(i) -center[1])/100))
	    tmpB[i][0] = 100 /(1+ np.exp(-cont[2]*(float(i) -center[2])/100))

	for i in range(256):
		if tmpR[255][0]-tmpR[0][0]!=0:
			lookUpTableR[i][0] = 255*(tmpR[i][0]-tmpR[0][0])/(tmpR[255][0]-tmpR[0][0])
		if tmpG[255][0]-tmpG[0][0]!=0:
			lookUpTableG[i][0] = 255*(tmpG[i][0]-tmpG[0][0])/(tmpG[255][0]-tmpG[0][0])
		if tmpB[255][0]-tmpB[0][0]!=0:
			lookUpTableB[i][0] = 255*(tmpB[i][0]-tmpB[0][0])/(tmpB[255][0]-tmpB[0][0])
		
	
	lookUpTable = cv2.merge((lookUpTableB,lookUpTableG,lookUpTableR))
#	print(lookUpTable[0])
	return lookUpTable

def addLUT(lut1,lut2):
	lookUpTableB = np.zeros((256, 1), dtype = 'uint8')
	lookUpTableG = np.zeros((256, 1), dtype = 'uint8')
	lookUpTableR = np.zeros((256, 1), dtype = 'uint8')
	for i in range(256):
		lookUpTableB[i][0] = lut2[lut1[i][0][0]][0][0]
		lookUpTableG[i][0] = lut2[lut1[i][0][1]][0][1]
		lookUpTableR[i][0] = lut2[lut1[i][0][2]][0][2]
	lookUpTable = cv2.merge((lookUpTableB,lookUpTableG,lookUpTableR))
	return lookUpTable

maskpt =  [[0,0], [0,720], [1280, 720], [1280,0]]
drag = -1
pickup_mode = 'none'

# マウスイベント時に処理を行う
def mouse_event(event, x, y, flags, param):
	global drag
	if event==cv2.EVENT_LBUTTONUP:
		drag = -1

	if event==cv2.EVENT_LBUTTONDOWN:
		for i,pt in enumerate(maskpt):
			if np.linalg.norm(np.array(pt)-np.array([x*2,y*2]))<12:
				drag = i
				break

	if drag!=-1 and event==cv2.EVENT_MOUSEMOVE:
		maskpt[drag]= [x*2,y*2]

def imshow_scale(name,img,scale):
	scale_img = cv2.resize(img,(int(img.shape[1]*scale),int(img.shape[0]*scale)))
	cv2.imshow(name,scale_img)

def open_comport(port,speed):
	try :
		ser = sr.Serial(port,speed)
	except serial.SerialException:
		print("ポートが開けないようです") 
		return -1
	return ser

def send_thread(ser):
	global data
	while True:
		print("senddata:",data)
		ser.write(data)
		time.sleep(5)


def main_th():
	global cont
	#cap = cv2.VideoCapture('http://192.168.11.100:8080/?action=stream')
	while True:
	#	org_frame = cv2.imread('test.jpg')
		org_frame = cv2.imread('seg_img/img1.jpg')
		#for i in range(15):
		#	cap.read()
		#ret, org_frame = cap.read()

		size = 720,1280,3
		back_mask_img = np.zeros(size, dtype=np.uint8)
		contours = np.array( maskpt )
		cv2.fillPoly(back_mask_img, pts =[contours], color=(255,255,255))
		#cv2.imshow("back mask", back_mask_img)

		org_frame[back_mask_img==0] = [0]


		"""	
		lut1= makeBrightLUT(bright)
		lut2 = makeContrastLUT(cont,cont_c)
		lut3 = makeGammaLUT(gamma)
		lut = addLUT(lut1,lut2)
		lut = addLUT(lut,lut3)
		org_frame = cv2.LUT(org_frame,lut)
		"""

#		cv2.imshow("org image", org_frame)

#		gamma = makeGammaLUT(1.7)
#		org_frame = cv2.LUT(org_frame, gamma)

		hsvimg = cv2.cvtColor(org_frame, cv2.COLOR_BGR2HSV)
		hsvchannel = cv2.split(hsvimg)
		
	#	gamma = makeGammaLUT(1.3)
	#	hsvchannel[1] = cv2.LUT(hsvchannel[1], gamma)

		#cont = makeSContrastLUT(s[0],s[1])  # Sチャンネルコントラスト
#		gamma = makeGammaLUT(2.0)
		hsvchannel[1] = cv2.LUT(hsvchannel[1], svpanel.SLUT)
		hsvchannel[2] = cv2.LUT(hsvchannel[2], svpanel.VLUT)

#		cont = makeContrastLUT(0.1,60)  # Vチャンネルコントラスト
#		hsvchannel[2] = cv2.LUT(hsvchannel[2], cont)

		org_frame = cv2.merge((hsvchannel[0],hsvchannel[1] ,hsvchannel[2])  )
		org_frame = cv2.cvtColor(org_frame, cv2.COLOR_HSV2BGR)

		ui_frame = org_frame.copy()
		ui_frame = cv2.resize(ui_frame,(int(ui_frame.shape[1]/2),int(ui_frame.shape[0]/2)))
		for pt in maskpt:
			cv2.circle(ui_frame, center =(int(pt[0]/2),int(pt[1]/2)), radius = 6 , color = (0,0,255), thickness=2)
		cv2.imshow("UI image", ui_frame)
		cv2.setMouseCallback("UI image", mouse_event)

	#	cv2.imshow("h image", hsvchannel[0])
	#	cv2.imshow("s image", hsvchannel[1])
	#	cv2.imshow("v image", hsvchannel[2])
		
		ret, vmask = cv2.threshold(hsvchannel[2],160,255,cv2.THRESH_BINARY)
	#	vmask = cv2.adaptiveThreshold(hsvchannel[2],255,cv2.ADAPTIVE_THRESH_MEAN_C,\
	#           cv2.THRESH_BINARY,513,2)


	#	cv2.imshow("v mask", vmask)

	#	ret, chan1mask = cv2.threshold(hsvchannel[0],30,255,cv2.THRESH_BINARY)
	#	ret, chan1mask2 = cv2.threshold(hsvchannel[0],90,255,cv2.THRESH_BINARY_INV)	
	#	mask = cv2.bitwise_and(chan1mask,chan1mask2)
	#	mask = cv2.bitwise_and(mask,vmask)
		g_mask = np.zeros(hsvchannel[0].shape, dtype=np.uint8)
		st,ed = svpanel.getGreenRange()
		g_mask[( (hsvchannel[0] >st/2 ) &  (hsvchannel[0] < ed/2) )& ((hsvchannel[1] > 60) & (hsvchannel[2] > 90))] = 255

		r_mask = np.zeros(hsvchannel[0].shape, dtype=np.uint8)
		st,ed = svpanel.getRedRange()
		if(st<ed):
			r_mask[( (hsvchannel[0] >st/2 ) &  (hsvchannel[0] < ed/2) )& ((hsvchannel[1] > 60) & (hsvchannel[2] > 90))] = 255
		else:
			r_mask[(((hsvchannel[0] >= 0) &  (hsvchannel[0] < ed/2)) |\
			 ((hsvchannel[0] >st/2 ) &  (hsvchannel[0] <= 180))) &  ((hsvchannel[1] > 60) & (hsvchannel[2] > 90))] = 255

		b_mask = np.zeros(hsvchannel[0].shape, dtype=np.uint8)
		st,ed = svpanel.getBlueRange()
		b_mask[((hsvchannel[0] >st/2) &  (hsvchannel[0] < ed/2)) &  ((hsvchannel[1] > 60) & (hsvchannel[2] > 90) )] = 255

		y_mask = np.zeros(hsvchannel[0].shape, dtype=np.uint8)
		st,ed = svpanel.getYellowRange()
		y_mask[((hsvchannel[0] >st/2 ) &  (hsvchannel[0] < ed/2)) &  ((hsvchannel[1] > 60) & (hsvchannel[2] > 90) )] = 255

		bk_mask = np.zeros(hsvchannel[0].shape, dtype=np.uint8)
		bv,bs = svpanel.getBlackVS()
		bk_mask[ (hsvchannel[1] < bs) & (hsvchannel[2] < bv)] = 255

		mask = cv2.bitwise_or(b_mask,g_mask)
		mask = cv2.bitwise_or(mask,r_mask)
		mask = cv2.bitwise_or(mask,y_mask)
		mask = cv2.bitwise_or(mask,bk_mask)
		#cv2.imshow("y mask", y_mask)
		
		masks = (b_mask,g_mask,r_mask,y_mask,bk_mask)

		h_s = hsvchannel[1]*(mask/255.0) # mask以外のS値を0に
	#	h_s = hsvchannel[1]*(hsvchannel[2]/255)
		h_s = h_s.astype('uint8')
	#	cont = makeContrastLUT(1.8)
	#	h_s = cv2.LUT(h_s, cont).astype('uint8')
		ret, h_s_bin = cv2.threshold(h_s,20,255,cv2.THRESH_BINARY)
		
		newimg = cv2.merge((hsvchannel[0], h_s, hsvchannel[2]))
		drawimg = cv2.cvtColor(newimg, cv2.COLOR_HSV2BGR)
		
		draw_line_col = ((255,0,0),(0,255,0),(0,0,255),(0,255,255),(100,100,100))
		for i, cur_mask in enumerate(masks):
			contours, _ = cv2.findContours(cur_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
			rects = []
			for contour in contours:
				area = cv2.contourArea(contour,False)
				rect = cv2.boundingRect(contour)
				rectarea = rect[2]*rect[3]
				if area<330 or area>3500 or rect[2]<15 or rect[3]<15 :
					continue
				#approx = cv2.convexHull(contour)
				rects.append(rect)
				cv2.rectangle(drawimg, rect,draw_line_col[i], 2,6)    
		
		
		#cv2.imshow("h_s", h_s)

		#draw_half_image = cv2.resize(drawimg,(int(drawimg.shape[1]/2),int(drawimg.shape[0]/2)))
		#cv2.imshow("result image", draw_half_image)
		imshow_scale("result image",drawimg,0.5)

		k = cv2.waitKey(10);
		if k == ord('q'):
			camera_on = False
			break;
		
def color_red(n):
	global gamma
	gamma[0] = float(n)
	
def color_green(n):
	global gamma
	gamma[1] = float(n)

def color_blue(n):
	global gamma
	gamma[2] = float(n)

def cont_red(n):
	global cont
	cont[0] = float(n)
	
def cont_green(n):
	global cont
	cont[1] = float(n)

def cont_blue(n):
	global cont
	cont[2] = float(n)
def cont_c_red(n):
	global cont_c
	cont_c[0] = float(n)
	
def cont_c_green(n):
	global cont_c
	cont_c[1] = float(n)

def cont_c_blue(n):
	global cont_c
	cont_c[2] = float(n)
	
def bri_red(n):
	global bri
	bright[0] = float(n)
	
def bri_green(n):
	global bri
	bright[1] = float(n)

def bri_blue(n):
	global bri
	bright[2] = float(n)

def cont_s(n):
	global s
	s[0] = float(n)
def cont_s_c(n):
	global s
	s[1] = float(n)


gamma = [1.0,1.0,1.0]
cont = [0,0,0]
cont_c = [128,128,128]
bright = [0,0,0]

s = [0,128]
		
root = tk.Tk()
root.title(u"カラー調整")
root.geometry("800x400")
"""
cusf=tk.Frame()
cusf.pack(fill=tk.BOTH, padx=10, pady=10)


l1=tk.Label(cusf, text='赤γ:', anchor=tk.W, fg='red')
l1.grid(row=0,column=0,sticky=tk.W)
l2=tk.Label(cusf, text='緑γ:', anchor=tk.W , fg='green')
l2.grid(row=1,column=0,sticky=tk.W)
l3=tk.Label(cusf, text='青γ:', anchor=tk.W, fg='blue')
l3.grid(row=2,column=0,sticky=tk.W)
scale1 = tk.Scale(cusf, length=400,orient='h',from_=0.0, to=2.4, resolution=0.01, tickinterval=0.2, command=color_red)
scale1.grid(row=0,column=1)
scale2 = tk.Scale(cusf, length=400,orient='h',from_=0.0, to=2.4, resolution=0.01, tickinterval=0.2, command=color_green)
scale2.grid(row=1,column=1)
scale3 = tk.Scale(cusf, length=400,orient='h',from_=0.0, to=2.4, resolution=0.01, tickinterval=0.2, command=color_blue)
scale3.grid(row=2,column=1)

scale1.set(1.0)
scale2.set(1.0)
scale3.set(1.0)

cont_l1=tk.Label(cusf, text='赤コントラスト:', anchor=tk.W, fg='red')
cont_l1.grid(row=3,column=0,sticky=tk.W)
cont_l2=tk.Label(cusf, text='緑コントラスト:', anchor=tk.W , fg='green')
cont_l2.grid(row=4,column=0,sticky=tk.W)
cont_l3=tk.Label(cusf, text='青コントラスト:', anchor=tk.W, fg='blue')
cont_l3.grid(row=5,column=0,sticky=tk.W)
cont_scale1 = tk.Scale(cusf, length=400,orient='h',from_=0.0, to=10, resolution=0.1, tickinterval=2, command=cont_red)
cont_scale1.grid(row=3,column=1)
cont_scale2 = tk.Scale(cusf, length=400,orient='h',from_=0.0, to=10, resolution=0.1, tickinterval=2, command=cont_green)
cont_scale2.grid(row=4,column=1)
cont_scale3 = tk.Scale(cusf, length=400,orient='h',from_=0.0, to=10, resolution=0.1, tickinterval=2, command=cont_blue)
cont_scale3.grid(row=5,column=1)

cont_scale1.set(0.0)
cont_scale2.set(0.0)
cont_scale3.set(0.0)


cont_c_l1=tk.Label(cusf, text='赤センター:', anchor=tk.W, fg='red')
cont_c_l1.grid(row=3,column=2,sticky=tk.W)
cont_c_l2=tk.Label(cusf, text='緑センター:', anchor=tk.W , fg='green')
cont_c_l2.grid(row=4,column=2,sticky=tk.W)
cont_c_l3=tk.Label(cusf, text='青センター:', anchor=tk.W, fg='blue')
cont_c_l3.grid(row=5,column=2,sticky=tk.W)
cont_c_scale1 = tk.Scale(cusf, length=400,orient='h',from_=0, to=255, resolution=1, tickinterval=32, command=cont_c_red)
cont_c_scale1.grid(row=3,column=3)
cont_c_scale2 = tk.Scale(cusf, length=400,orient='h',from_=0, to=255, resolution=1, tickinterval=32, command=cont_c_green)
cont_c_scale2.grid(row=4,column=3)
cont_c_scale3 = tk.Scale(cusf, length=400,orient='h',from_=0, to=255, resolution=1, tickinterval=32, command=cont_c_blue)
cont_c_scale3.grid(row=5,column=3)

cont_c_scale1.set(cont_c[0])
cont_c_scale2.set(cont_c[1])
cont_c_scale3.set(cont_c[2])


bri_l1=tk.Label(cusf, text='赤ブライトネス:', anchor=tk.W, fg='red')
bri_l1.grid(row=6,column=0,sticky=tk.W)
bri_l2=tk.Label(cusf, text='緑ブライトネス:', anchor=tk.W , fg='green')
bri_l2.grid(row=7,column=0,sticky=tk.W)
bri_l3=tk.Label(cusf, text='青ブライトネス:', anchor=tk.W, fg='blue')
bri_l3.grid(row=8,column=0,sticky=tk.W)
bri_scale1 = tk.Scale(cusf, length=400,orient='h',from_=-50.0, to=50, resolution=1, tickinterval=5, command=bri_red)
bri_scale1.grid(row=6,column=1)
bri_scale2 = tk.Scale(cusf, length=400,orient='h',from_=-50.0, to=50, resolution=1, tickinterval=5, command=bri_green)
bri_scale2.grid(row=7,column=1)
bri_scale3 = tk.Scale(cusf, length=400,orient='h',from_=-50.0, to=50, resolution=1, tickinterval=5, command=bri_blue)
bri_scale3.grid(row=8,column=1)

bri_scale1.set(0.0)
bri_scale2.set(0.0)
bri_scale3.set(0.0)


s_l1=tk.Label(cusf, text='彩度:', anchor=tk.W, fg='red')
s_l1.grid(row=0,column=2,sticky=tk.W)
s_scale1 = tk.Scale(cusf, length=400,orient='h',from_=0.0, to=10, resolution=0.1, tickinterval=2, command=cont_s)
s_scale1.grid(row=0,column=3)
s_c_l1=tk.Label(cusf, text='彩度センター:', anchor=tk.W, fg='red')
s_c_l1.grid(row=1,column=2,sticky=tk.W)
s_c_scale1 = tk.Scale(cusf, length=400,orient='h',from_=0, to=255, resolution=1, tickinterval=32, command=cont_s_c)
s_c_scale1.grid(row=1,column=3)

s_c_scale1.set(128)
s_scale1.set(0.0)
"""

svpanel = SV_Panel()
svpanel.makePanel()

main_th = th.Thread(target=main_th)
main_th.setDaemon(True)
main_th.start()

bt = Bluetooth("COM40",9600)
bt.set_dataln("t0")
ret = bt.open_comport()
if ret==True:
	print("open完了")
	bt.start_send_thread()
	#bt_th = th.Thread(target=bluetooth.send_thread())
	#bt_th.start()

root.mainloop()

