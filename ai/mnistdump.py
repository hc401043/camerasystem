import os
from PIL import Image
import tensorflow as tf
import input_data
import numpy as np

def save(data, index, num):
    img = Image.new("L", (28, 28))
    pix = img.load()
    for i in range(28):
        for j in range(28):
            pix[i, j] = int(data[i+j*28]*256)
    img2 = img.resize((280, 280))
    filename = str(num) + "/test" + "{0:04d}".format(index) + ".png"
    img2.save(filename)
    print (filename)

def main():
    mnist = input_data.read_data_sets("./MNIST_data/", one_hot=True)



    for i in range(10):
        dirname = str(i)
        if os.path.isdir(dirname) is False:
            os.mkdir(dirname)
    for i in range(100):
        img = mnist.test.images[i]
        label = np.argmax(mnist.test.labels[i])
        save(img, i, label)



if __name__ == '__main__':
    main()