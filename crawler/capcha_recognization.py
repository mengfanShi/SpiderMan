# coding:utf-8
import os
os.environ['KERAS_BACKEND']='theano'
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential,load_model
from keras.layers import Convolution2D, MaxPooling2D
from keras.layers import Activation, Dropout, Flatten, Dense
from bs4 import BeautifulSoup
import time
import requests
import numpy as np
from PIL import Image
import shutil
import re

# dimensions of our images.
img_width, img_height = 60, 30

crop_weights = './cropWeights.h5'
class_weights = './classWeights.h5'
crop_model = './cropModel.h5'
class_model = './classModel.h5'
nb_train_samples = 100
nb_validation_samples = 10
nb_epoch = 3000
mapList = ['3','5','6','7','8','9','A','B','D','E','F','G','H','J','K','M','N','P','R','S','T','U','V','X','Y']
mapArray = np.array(mapList)


def crop(im):
    step = 1
    boxList = []
    for i in range(121):
        boxList.append((step*i, 0, 30+step*i, 60))
    if not os.path.exists('./captchaTemp/data'):
        os.mkdir('captchaTemp')
        os.mkdir('./captchaTemp/data')
    count = 0
    for each in boxList:
        region = im.crop(each)
        region.save('captchaTemp/data/' + str(count) + '.png')
        count += 1

def predict(cropModel,classModel):
    datagenCrop = ImageDataGenerator(rescale=1./255, zca_whitening=True)
    datagenClass = ImageDataGenerator(rescale=1./255, zca_whitening=True)
    cropGenerator = datagenCrop.flow_from_directory(
        'captchaTemp',
        color_mode='grayscale',
        shuffle = False,
        target_size=(60,30))
    cropFilenames = cropGenerator.filenames
    predictCrop = cropModel.predict_generator(cropGenerator,121)
    # sorting images
    maping = []
    for imName in cropFilenames:
        maping.append(int(re.sub('\D*','',imName)))
    goodArr = predictCrop[:,1]
    print('predictCrop: {}'.format(goodArr))
    index = np.argsort(goodArr).tolist()
    finalIndex = [maping[p] for p in index]
    index = []
    index = finalIndex
    print('index: {}'.format(index))
    target = index[-5:-1]
    print('target: {}'.format(target))
    index = index[:-4]
    checkAndReplace(index, target, 18)
    target.sort()
    if os.path.exists('./tobe_classfied'):
        shutil.rmtree('./tobe_classfied')
    os.mkdir('tobe_classfied')
    os.mkdir('./tobe_classfied/data')
    imList = []
    for each in target:
        imList.append(str(each) + '.png')
    print(imList)
    for each in imList:
        temp = Image.open('./captchaTemp/data/' + each)
        temp.save('./tobe_classfied/data/' + each)
    classGenerator = datagenClass.flow_from_directory(
        'tobe_classfied',
        color_mode='grayscale',
        shuffle = False,
        target_size=(60,30))
    predictClass = classModel.predict_generator(classGenerator,4)
    classFilenames = classGenerator.filenames
    sortedFilenames = os.listdir('./tobe_classfied/data')
    sortedFilenames.sort(key=lambda x : int(x[:-4]))
    print('predictLcass: {}'.format(predictClass))
    print('classFilenames:{}'.format(classFilenames))
    print('sortedFilenames:{}'.format(sortedFilenames))
    classIndex = []
    temp = [0,0,0,0]
    result = predictClass.argmax(axis = 1)
    result.tolist()
    print('result:{}'.format(result))
    for each in classFilenames:
        classIndex.append(sortedFilenames.index(os.path.basename(each)))
    for each in classIndex:
        temp[each] = result[classIndex.index(each)]
    result = temp
    print('result: {}'.format(result))
    finalClass = mapArray[result]
    print(finalClass)
    finalClass.tolist()
    captcha = ''.join(finalClass)
    print('captcha:{}'.format(captcha))
    return captcha

def checkAndReplace(index,target,distance):
    state = 1
    for i in range(0,len(target)-1):
        for j in range(i+1,len(target)):
            if abs(target[i] - target[j]) < distance:
                print('i: {}, j: {}'.format(str(i),str(j)))
                print('replace {} '.format(str(target[j])))
                target[j] = index.pop()
                print('target:{}'.format(str(target)))
                state *= 0
            else:
                state *=1
    while (state == 0):
        state = 1
        for i in range(0,len(target)-1):
            for j in range(i+1,len(target)):
                if abs(target[i] - target[j]) < distance:
                    print('i: {}, j: {}'.format(str(i),str(j)))
                    print('replace {} '.format(str(target[j])))
                    target[j] = index.pop()
                    print('target:{}'.format(str(target)))
                    state *= 0
                else:
                    state *=1

if __name__ == '__main__':
    cropModel = load_model(crop_model)
    classModel = load_model(class_model)
    im = Image.open('captcha.jpg')
    crop(im)
    capcha = predict(cropModel,classModel)