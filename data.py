# Used to gather and augment the dataset.
# Run this file in the same directory as 'train.csv'
# Also, make sure your training images are stored in './train'
import math
import random
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from pandas import read_csv
from collections import Counter
from PIL import Image
from keras.preprocessing.image import load_img, random_rotation, random_shift, random_shear, random_zoom,img_to_array
from keras.applications.imagenet_utils import preprocess_input
from sklearn.model_selection import train_test_split


class DataGrabber():
    
    def __init__(self):
        self.unused_id = 0
        self.whale2id = {}
        self.train_df = pd.read_csv('train.csv')
        self.train_df.head()

    def get_data(self):
        Y = np.zeros((self.train_df.shape[0],),dtype=int)
        X = np.zeros((self.train_df.shape[0],100,100,3))
        for idx,row in self.train_df.iterrows():
            img = load_img(f"train/{row['Image']}", target_size=(100,100,3))
            img_arr = img_to_array(img)
            img_arr = preprocess_input(img_arr)
            X[idx] = img_arr
            label = row['Id']
            if not label in self.whale2id:
                self.whale2id[label] = self.unused_id
                self.unused_id += 1
            Y[idx] = int(self.whale2id[label])
            if idx%500 == 0:
                print(f"Processing image {idx}")
        tmp = np.zeros((Y.size, int(Y.max()+1)))
        tmp[np.arange(Y.size), Y] = 1
        Y = tmp
        X_train, X_test, y_train, y_test = train_test_split(X,Y,test_size=0.1)
        return (X_train, X_test, y_train, y_test)

    def augment_image(self, img_arr):
        img_arr = random_rotation(img_arr, 18, row_axis=0, col_axis=1, channel_axis=2, fill_mode='nearest')
        img_arr = random_shear(img_arr, intensity=0.4, row_axis=0, col_axis=1, channel_axis=2, fill_mode='nearest')
        img_arr = random_zoom(img_arr, zoom_range=(0.9, 2.0), row_axis=0, col_axis=1, channel_axis=2, fill_mode='nearest')
        if img_arr.shape[-1] == 3:
            img_arr = self.random_greyscale(img_arr, 0.4)
                
        return img_arr

    def random_greyscale(self,img,p):
        if random.random() < p:
            return np.dot(img[...,:3],[0.299,0.587,0.114])[...,np.newaxis]
        return img

    def augment_dataset(self,X,y,n_aug):
        y_aug = np.zeros((self.train_df.shape[0]*n_aug,y.shape[1]),dtype=int)
        X_aug = np.zeros((self.train_df.shape[0]*n_aug,100,100,3))
        for idx, img in enumerate(X):
            label = y[idx]
            for _ in range(n_aug):
                img_arr = img_to_array(img)
                X_aug[idx] = self.augment_image(img_arr)
                y_aug[idx] = label
        return (X_aug, y_aug)

class Visualizer():
    
    def __init__(self):
        pass
    
    def plot_images_for_filenames(self,filenames, labels, fname, rows=4):
        imgs = [plt.imread(f'train/{filename}') for filename in filenames]
        return self.plot_images(imgs, labels, fname, rows)


    def plot_images(self,imgs, labels, fname, rows=4):
        # Set figure to 13 inches x 8 inches
        figure = plt.figure(figsize=(13, 8))

        cols = len(imgs) // rows + 1

        for i in range(len(imgs)):
            subplot = figure.add_subplot(rows, cols, i + 1)
            subplot.axis('Off')
            if labels:
                subplot.set_title(labels[i], fontsize=16)
                plt.imshow(imgs[i], cmap='gray')
        plt.savefig(fname)

def plot_some_images():
    vis = Visualizer()
    dg = DataGrabber()
    train_df = dg.train_df()
    rand_rows = train_df.sample(frac=1.)[:20]
    imgs = list(rand_rows['Image'])
    labels = list(rand_rows['Id'])
    vis.plot_images_for_filenames(imgs,labels,'random_images.png')

def plot_categlory_histogram():
    vis = Visualizer()
    dg = DataGrabber()
    train_df = dg.train_df()
    size_buckets = Counter(train_df['Id'].value_counts().values)

    plt.figure(figsize=(10, 6))
    
    plt.bar(range(len(size_buckets)), list(size_buckets.values())[::-1], align='center')
    plt.xticks(range(len(size_buckets)), list(size_buckets.keys())[::-1])
    plt.title("Num of categories by images in the training set")
    
    plt.savefig('categlories.png')


def save_datasets():
    dg = DataGrabber()
    X_train, X_test, y_train, y_test = dg.get_data()
    #pickle.dump((X_train, y_train, X_test, y_test), open('data.pickle','wb+'))
    X_train, y_train = dg.augment_dataset(X_train, y_train, n_aug=5)
    print(X_train.shape)
    print(y_train.shape)
    # I was not able to do this on my machine bc file was over 4 Gib w/ n_aug=5
    #pickle.dump((X_train, y_train, X_test, y_test), open('augmented_data.pickle','wb+'))

def get_augmented_dataset(n_aug=5):
    dg = DataGrabber()
    X_train, y_train, X_test, y_test = pickle.load(open('data.pickle','rb+'))
    X_train, y_train = dg.augment_dataset(X_train, y_train, n_aug=n_aug)
    return X_train, y_train, X_test, y_test

def get_dataset():
    dg = DataGrabber()
    X_train, y_train, X_test, y_test = pickle.load(open('data.pickle','rb+'))
    return X_train, y_train, X_test, y_test


if __name__ == '__main__':
    plot_some_images()
    plot_categlory_histogram()
    save_datasets()
