from ImageProcess import ImageProcess
from abc import ABCMeta, abstractmethod

class ImageExtraction(ImageProcess):

    __metaclass__ = ABCMeta

    def __init__(self,panel,imgprocess):
        super(ImageExtraction,self).__init__(panel)
        self.imgprocess = imgprocess

    
    

