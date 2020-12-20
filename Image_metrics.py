import csv
import os

import cv2
import numpy as np

PATH = os.path.abspath(os.getcwd())


def getListOfNames(path, ext=".png"):
    all_imgs = list()

    for file in os.listdir(path):
        if file.endswith(ext):
            all_imgs.append(os.path.join(path, file))
            print(os.path.join(path, file))
    return all_imgs


def calcContrast(names):
    res = list()
    for name in names:
        img = cv2.imread(name)

        # compute min and max of
        min = int(np.min(img))
        max = int(np.max(img))
        # compute contrast
        contrast = (max - min) / (max + min)
        res.append(contrast)
    return res


def calc_RMS_Contrast(names):
    res = list()
    for name in names:
        img = cv2.imread(name)

        contrast = img.std()
        res.append(contrast)
    return res


def calc_CustomMetric_a(names):
    res = list()
    for name in names:
        img = cv2.imread(name)
        block_y = len(img)
        block_x = len(img[0])
        p = block_x * block_y
        avg = 0
        avg_pow = 0
        dsp = 0
        sum = 0
        sum2 = np.int64(0)
        for x in range(block_x):
            for y in range(block_y):
                sum = sum + img[y][x][0]
                sum2 = sum2 + (img[y][x][0] ** 2)
                # print(x, y)

        avg = sum / (block_x * block_y)
        avg_pow = (int(sum2) / (block_x * block_y))
        dsp = avg_pow - avg ** 2
        d = avg

        q = 0

        for x in range(block_x):
            for y in range(block_y):
                if img[y][x][0] > avg:
                    q = q + 1

        try:
            # среднее - (СКО * (долю пикселей больше среднего)**0.5 )
            a = int(round(avg - (dsp ** 0.5) * ((q / (p - q)) ** 0.5)))
            b = int(round(avg + (dsp ** 0.5) * (((p - q) / q) ** 0.5)))
            if a < 1:
                a = 0
            if b < 1:
                b = 0

            res.append(a)
        except ZeroDivisionError:
            a = b = int(round(avg))

    return res


def calc_CustomMetric_b(names):
    res = list()
    for name in names:
        img = cv2.imread(name)
        block_y = len(img)
        block_x = len(img[0])
        p = block_x * block_y
        avg = 0
        avg_pow = 0
        dsp = 0
        sum = 0
        sum2 = np.int64(0)
        for x in range(block_x):
            for y in range(block_y):
                sum = sum + img[y][x][0]
                sum2 = sum2 + (img[y][x][0] ** 2)
                # print(x, y)

        avg = sum / (block_x * block_y)
        avg_pow = (int(sum2) / (block_x * block_y))
        dsp = avg_pow - avg ** 2
        d = avg

        q = 0

        for x in range(block_x):
            for y in range(block_y):
                if img[y][x][0] > avg:
                    q = q + 1

        try:
            # среднее - (СКО * (отношение пикселей выше среднего к пикселям ниже среднего)**0.5 )
            a = int(round(avg - (dsp ** 0.5) * ((q / (p - q)) ** 0.5)))
            # среднее + (СКО * (отношение пикселей ниже среднего к пикселям выше среднего)**0.5 )
            b = int(round(avg + (dsp ** 0.5) * (((p - q) / q) ** 0.5)))
            if a < 1:
                a = 0
            if b < 1:
                b = 0

            res.append(b)
        except ZeroDivisionError:
            a = b = int(round(avg))

    return res


def calc_CustomMetric(names):
    res = list()
    for name in names:
        img = cv2.imread(name)
        block_y = len(img)
        block_x = len(img[0])
        p = block_x * block_y
        avg = 0
        avg_pow = 0
        dsp = 0
        sum = 0
        sum2 = np.int64(0)
        for x in range(block_x):
            for y in range(block_y):
                sum = sum + img[y][x][0]
                sum2 = sum2 + (img[y][x][0] ** 2)
                # print(x, y)

        avg = sum / (block_x * block_y)
        avg_pow = (int(sum2) / (block_x * block_y))
        dsp = avg_pow - avg ** 2
        d = avg

        q = 0

        for x in range(block_x):
            for y in range(block_y):
                if img[y][x][0] > avg:
                    q = q + 1

        try:
            a = int(round(avg - (dsp ** 0.5) * ((q / (p - q)) ** 0.5)))
            b = int(round(avg + (dsp ** 0.5) * (((p - q) / q) ** 0.5)))
            if a < 1:
                a = 0
            if b < 1:
                b = 0

            res.append(a / b)
        except ZeroDivisionError:
            a = b = int(round(avg))

    return res


def WriteToFile(folder, *args):
    names = getListOfNames(PATH + folder)

    output = list()
    for func in args:
        res = func(names)
        output.append(res)

    with open(PATH + folder + "\out.csv", "w") as f:
        wr = csv.writer(f)
        wr.writerows(output)
