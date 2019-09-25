
class Setting:
    def __init__(self,fname):
        self.fpath = fname
        self.s_center=128
        self.s_con=0
        self.v_center=128
        self.v_con=0
        self.red_range_center = 5
        self.green_range_center = 135
        self.blue_range_center = 230
        self.yellow_range_center = 60
        self.red_range=20
        self.green_range=40
        self.blue_range=40
        self.yellow_range=20
        self.black_v=128
        self.black_s=80
        self.maskpt =  [[0,0], [0,720], [1280, 720], [1280,0]]
        self.nummaskpt = [[0,340],[500,720]]
        self.course='L'

    
    def read_settings(self):
        try:
            with open(self.fpath,"r") as f:
                lines = f.readlines()
                for line in lines:
                    items = line.split(":")
                    params = items[1].split(",")
                    if items[0]=="S":
                        self.s_center = float(params[0])
                        self.s_con = float(params[1])
                    elif items[0]=="V":
                        self.v_center=float(params[0])
                        self.v_con=float(params[1])
                    elif items[0]=="R":
                        self.red_range_center = int(params[0])
                        self.red_range = int(params[1])
                    elif items[0]=="G":
                        self.green_range_center = int(params[0])
                        self.green_range = int(params[1])
                    elif items[0]=="B":
                        self.blue_range_center = int(params[0])
                        self.blue_range = int(params[1])
                    elif items[0]=="Y":
                        self.yellow_range_center = int(params[0])
                        self.yellow_range = int(params[1])
                    elif items[0]=="Bk":
                        self.black_v=int(params[0])
                        self.black_s=int(params[1])
                    elif items[0]=="TL":
                        self.maskpt[0] = [int(params[0]),int(params[1])]
                    elif items[0]=="TR":
                        self.maskpt[1] = [int(params[0]),int(params[1])]
                    elif items[0]=="BR":
                        self.maskpt[2] = [int(params[0]),int(params[1])]
                    elif items[0]=="BL":
                        self.maskpt[3] = [int(params[0]),int(params[1])]
                    elif items[0]=="NTL":
                        self.nummaskpt[0] = [int(params[0]),int(params[1])]
                    elif items[0]=="NBR":
                        self.nummaskpt[1] = [int(params[0]),int(params[1])]
                    elif items[0]=="Course":
                        self.course=params[0][0]

        except IOError:
            print("設定ファイルが開けないのでデフォルト設定を使います")

    def save_settings(self):

        try:

            with open(self.fpath,"w") as f:
                print("S:{},{}\n".format(self.s_center,self.s_con))
                f.write("S:{},{}\n".format(self.s_center,self.s_con))
                f.write("V:{},{}\n".format(self.v_center,self.v_con))
                f.write("R:{},{}\n".format(self.red_range_center,self.red_range))
                f.write("G:{},{}\n".format(self.green_range_center,self.green_range))
                f.write("B:{},{}\n".format(self.blue_range_center,self.blue_range))
                f.write("Y:{},{}\n".format(self.yellow_range_center,self.yellow_range))
                f.write("Bk:{},{}\n".format(self.black_v,self.black_s))
                f.write("TL:{},{}\n".format(self.maskpt[0][0],self.maskpt[0][1]))
                f.write("TR:{},{}\n".format(self.maskpt[1][0],self.maskpt[1][1]))
                f.write("BR:{},{}\n".format(self.maskpt[2][0],self.maskpt[2][1]))
                f.write("BL:{},{}\n".format(self.maskpt[3][0],self.maskpt[3][1]))
                f.write("NTL:{},{}\n".format(self.nummaskpt[0][0],self.nummaskpt[0][1]))
                f.write("NBR:{},{}\n".format(self.nummaskpt[1][0],self.nummaskpt[1][1]))
                f.write("Course:{}\n".format(self.course))

        except IOError:
            print("設定ファイルが保存できません")
