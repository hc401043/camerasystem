# -*- coding: utf-8 -*-

import cv2
import sys
import os

#TensorFlowをインポート
import tensorflow as tf
#MNISTデータのロード
#one hotとは配列の中で一つだけ1それ以外が0のこと
from . import input_data
basepath = os.path.dirname(__file__)

mnist = input_data.read_data_sets(basepath+"/MNIST_data/", one_hot=True)
import time
import os,sys
import numpy as np
from PIL import Image
from matplotlib import pylab as plt


#時間計測の開始
start = time.time()

sess = tf.InteractiveSession()

#プレースホルダーにてTFに計算を依頼
x = tf.placeholder("float", shape=[None, 784]) 
y_ = tf.placeholder("float", shape=[None, 10])

###############多層畳み込みネットワークの構築####################
#重みの初期化　tf.truncated_nomalではランダムな数値で初期化
def weight_variable(shape):
  initial = tf.truncated_normal(shape, stddev=0.1)
  return tf.Variable(initial)

def bias_variable(shape):
  initial = tf.constant(0.1, shape=shape)
  return tf.Variable(initial)

##畳み込み
def conv2d(x, W):
  return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')
##プーリング(次元削減)
#ksizeが2x2のピクセル枠作成
#stridesでピクセル枠の移動
def max_pool_2x2(x):
  return tf.nn.max_pool(x, ksize=[1, 2, 2, 1],
                        strides=[1, 2, 2, 1], padding='SAME')
                        
#######畳み込み層第1層############################
#5x5のフィルタにて32の特徴を計算
#2次元パッチサイズ、入力チャンネル数、出力チャンネル [5, 5, 1, 32]
W_conv1 = weight_variable( [5, 5, 1, 32] )
b_conv1 = bias_variable([32])

#xを4次元テンソルに作り変える
x_image = tf.reshape(x, [-1, 28, 28, 1])

#重みテンソルにバイアスを追加したものをReLU関数に適用(活性化)
#最大のプールをx_imageに畳み込む
h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)
h_pool1 = max_pool_2x2(h_conv1)

#######畳み込み層第2層############################
#5x5のパッチにて64の特徴を計算

W_conv2 = weight_variable( [5, 5, 32, 64])
b_conv2 = bias_variable([64])

h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)
h_pool2 = max_pool_2x2(h_conv2)

########密集接続層######################
W_fc1 = weight_variable( [7*7*64, 1024] )
b_fc1 = bias_variable( [1024] )
#reshapeにてベクトルに戻す
h_pool2_flat = tf.reshape(h_pool2, [-1,7*7*64] )
#行列演算と重みを加算し活性化させる
h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)

######ドロップアウト(過学習防止)#####################
#トレーニング中にドロップアウトを音、テスト中はオフに
keep_prob = tf.placeholder("float")
h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)

#########読みだし層#################
#ソフトマックス回帰を追加
W_fc2 = weight_variable( [1024, 10] )
b_fc2 = bias_variable( [10] )

#ソフトマックス回帰による正規化
y_conv = tf.nn.softmax(tf.matmul(h_fc1_drop, W_fc2) + b_fc2)

#####訓練######
#コスト関数'クロスエントロピー'の定義
cross_entropy = -tf.reduce_sum(y_*tf.log(y_conv))
#最急降下法の定義
train_step = tf.train.AdamOptimizer(1e-4).minimize(cross_entropy)

#train_step = tf.train.GradientDescentOptimizer(0.5).minimize(cross_entropy) # 別なサンプルから　GradientDescentOptimizer


#評価を行う(正解率の算出)
correct_predition = tf.equal(tf.argmax(y_conv, 1), tf.argmax(y_, 1))
accuracy = tf.reduce_mean(tf.cast(correct_predition, "float"))

#初期化
sess.run(tf.initialize_all_variables())
#学習データの保存
saver = tf.train.Saver()

if os.path.exists(basepath+"/CNN.ckpt.index"): # 学習データがある場合
  saver.restore(sess, basepath+"/CNN.ckpt") # データの読み込み
  print ("学習データを読み込みました")
else: #学習データがない場合→学習を開始
  print ("学習を開始します")
  for i in range(20000):
    batch = mnist.train.next_batch(50)
    if i%100 ==0:
        train_accuracy = accuracy.eval(feed_dict={x:batch[0], y_:batch[1], keep_prob: 1.0})
        print("学習回数： %d 回, training accuracy %g"%(i, train_accuracy))
    train_step.run(feed_dict={x:batch[0], y_:batch[1], keep_prob:0.5})
  ##学習パラメータの保存
  saver.save(sess, basepath+"/CNN.ckpt")

print("学習終了")  
#学習結果の表示
#print("この学習の正解率は %g です"%accuracy.eval(feed_dict={ x: mnist.test.images, y_:mnist.test.labels, keep_prob: 1.0}))



def guess_number(img):
	#画像を28x28に変換
  img = cv2.resize(img,(28,28))
  #cv2.imshow('img',img)
	
  #フロート型の行列に変換
  img = np.array(img, dtype=np.float32)
  #黒0~255白の画像データをMNISTのデータと同じ白0~1黒に変える
  img = 1 - np.array(img / 255)
  img = img.reshape(1, 784)
  #学習データと読み込んだ数値との比較を行う
  p = sess.run(y_conv, feed_dict={x:img, y_: [[0.0] * 10], keep_prob: 1.0})[0]
  #最も可能性のある数字を表示
  #print(p)
  #sys.stdout.write("\r可能性のある数字は%d" % np.argmax(p))
  #sys.stdout.flush()
  return np.argmax(p)