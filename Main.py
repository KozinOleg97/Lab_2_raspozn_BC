import copy
import math
import os
import random

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageChops  # Подключим необходимые библиотеки.

GILBERT_STATE = 1  # 1 - good; 2 - bad

orig_img_name = "AMDTest.bmp"

folder = "E:\Programming\Python\Lab_2_raspozn\\"

image = Image.open(orig_img_name)  # Открываем изображение.
draw = ImageDraw.Draw(image)  # Создаем инструмент для рисования.
width = image.size[0]  # Определяем ширину.
height = image.size[1]  # Определяем высоту.
print(width, height)
pix = image.load()  # Выгружаем значения пикселей.

#####Параметры#######################
CHANCE = 1 / 100  ########Вероятность ошибки#######
GILBERT_STATE_B_ERR_CHANCE = 1 / 4
GILBERT_STATE_CHANGE = 1 / 100
block_x = 1  #########Размер блока#######
block_y = 1  ########Размер блока########
block_numb = int(round(width * height / (block_x * block_y)))


def calc_block_avg(i, j, block_x, block_y):
    p = block_x * block_y
    avg = 0
    avg_pow = 0
    dsp = 0
    sum = 0
    sum2 = 0
    for x in range(block_x):
        for y in range(block_y):
            sum = sum + pix[i + x, j + y][0]
            sum2 = sum2 + (pix[i + x, j + y][0] ** 2)
            # print(x, y)

    avg = sum / (block_x * block_y)
    avg_pow = (sum2 / (block_x * block_y))
    dsp = avg_pow - avg ** 2
    d = avg

    q = 0

    for x in range(block_x):
        for y in range(block_y):
            if pix[i + x, j + y][0] > avg:
                q = q + 1

    try:
        a = int(round(avg - (dsp ** 0.5) * ((q / (p - q)) ** 0.5)))
        b = int(round(avg + (dsp ** 0.5) * (((p - q) / q) ** 0.5)))
        if a < 1:
            a = 0
        if b < 1:
            b = 0
    except ZeroDivisionError:
        a = b = int(round(avg))

    code = ""

    for x in range(block_x):
        for y in range(block_y):
            if pix[i + x, j + y][0] >= d:
                code = code + "1"
            else:
                code = code + "0"

    a = "{0000000:b}".format(a)
    b = "{0000000:b}".format(b)
    return [a, b, code]


def err(str, i):
    char = str[i]

    if char == "0":
        char = "1"
    else:
        char = "0"

    if len(str) > i:
        str = str[:i] + char + str[i + 1:]
    else:
        str = str[:i] + char

    return str


def gamble(chance):
    if random.random() < chance:
        return 1
    return 0


def gilbert(GILBERT_STATE):
    if GILBERT_STATE == 1:
        res = rnd_choice([GILBERT_STATE_CHANGE, 1 - GILBERT_STATE_CHANGE])
        if res == 1:
            g = gamble(CHANCE)
        if res == 0:  # perehod v B
            GILBERT_STATE = 0
            g = gamble(GILBERT_STATE_B_ERR_CHANCE)

    else:
        res = rnd_choice([GILBERT_STATE_CHANGE, 1 - GILBERT_STATE_CHANGE])
        if res == 1:
            g = gamble(GILBERT_STATE_B_ERR_CHANCE)
        if res == 0:  # perehod v B
            GILBERT_STATE = 1
            g = gamble(CHANCE)

    return g


def rnd_choice(array):
    # array = self.vectorToArray(vector)
    summ = sum(array)
    if summ < 1:
        array[0] += 1 - summ

    summ = sum(array)

    choice_index = np.random.choice(a=len(array), p=array, replace=False)

    return choice_index


def some_err(data):
    for blc in range(block_numb):
        cur_data = data[blc]
        code = cur_data[2]
        a = cur_data[0]
        b = cur_data[1]
        numb_code = len(code)
        numb_a = len(a)
        numb_b = len(b)

        for i in range(numb_a):
            if gamble(CHANCE):
                a = err(a, i)
        for i in range(numb_b):
            if gamble(CHANCE):
                b = err(b, i)
        for i in range(numb_code):
            if gamble(CHANCE):
                code = err(code, i)

        data[blc][0] = a
        data[blc][1] = b
        data[blc][2] = code
    return data


def gilbert_err(data):
    for blc in range(block_numb):
        cur_data = data[blc]
        code = cur_data[2]
        a = cur_data[0]
        b = cur_data[1]
        numb_code = len(code)
        numb_a = len(a)
        numb_b = len(b)

        for i in range(numb_a):
            if gilbert(GILBERT_STATE):
                a = err(a, i)
        for i in range(numb_b):
            if gilbert(GILBERT_STATE):
                b = err(b, i)
        for i in range(numb_code):
            if gilbert(GILBERT_STATE):
                code = err(code, i)

        data[blc][0] = a
        data[blc][1] = b
        data[blc][2] = code
    return data


######Распаковка###############
def unpack(data, img_orig):
    img = img_orig.copy()
    draw = ImageDraw.Draw(img)
    for blc in range(block_numb):
        cur_data = data[blc]
        code = cur_data[2]
        a = cur_data[0]
        b = cur_data[1]
        # print(a)
        a = int("0b" + a, base=2)
        b = int("0b" + b, base=2)

        # print(b)

        i = (blc * block_x) % width
        j = block_y * (blc * block_x // width)
        cur = 0
        for x in range(block_x):
            for y in range(block_y):
                if code[cur] == "1":
                    draw.point((i + x, j + y), (b, b, b))
                else:
                    draw.point((i + x, j + y), (a, a, a))
                cur = cur + 1

    return img
    # image.save(img_name + ".jpg", "JPEG")


def mse_diff(im1, im2):
    "Calculate the mean-square difference between two images"
    diff = ImageChops.difference(im1, im2)
    h = diff.histogram()
    sq = (value * ((idx % 256) ** 2) for idx, value in enumerate(h))
    sum_of_squares = sum(sq)
    mse = sum_of_squares / float(im1.size[0] * im1.size[1])
    return mse


def mse(img1, img2):
    img1 = img1.astype(np.float64) / 255.
    img2 = img2.astype(np.float64) / 255.
    mse = np.mean((img1 - img2) ** 2)
    return mse


def psnr(img1, img2):
    img1 = img1.astype(np.float64) / 255.
    img2 = img2.astype(np.float64) / 255.
    mse = np.mean((img1 - img2) ** 2)
    if mse == 0:
        return 100
    PIXEL_MAX = 255.0
    return 20 * math.log10(PIXEL_MAX / math.sqrt(mse))


def psnr_diff(mse):
    # mse = np.mean((original - contrast) ** 2)
    if mse == 0:
        return 100
    PIXEL_MAX = 255.0
    PSNR = 20 * math.log10(PIXEL_MAX / math.sqrt(mse))
    return PSNR


######оттенки серого########
"""for i in range(width):
    for j in range(height):
        a = pix[i, j][0]
        b = pix[i, j][1]
        c = pix[i, j][2]
        S = (a + b + c) // 3
        draw.point((i, j), (S, S, S))

image.save("gray.jpg", "JPEG")"""

# image_orig = image.copy()
# draw_orig = ImageDraw.Draw(image_orig)

# draw_orig = copy.deepcopy(draw)

########Упаковка#####
data = []
for blc in range(block_numb):
    i = (blc * block_x) % width
    j = block_y * (blc * block_x // width)
    # print(i)
    # print(j)
    # print("--")
    avg = 0
    avg2 = 0
    dsp = 0

    data.append(calc_block_avg(i, j, block_x, block_y))
###########Искажение##################
data3 = None
data2 = None
# data2 = some_err(copy.deepcopy(data))
# data3 = gilbert_err(copy.deepcopy(data))

# data3 = data2

data4 = copy.deepcopy(data)

#########Распаковка#######################
img_no_err = unpack(data4, image)
# img_err = unpack(data2, image)
# img_err_gilbert = unpack(data3, image)

img_no_err.save("img_no_err.bmp", "BMP")
# img_err_gilbert.save("img_gilbert.bmp", "BMP")
# img_err.save("img_err.bmp", "BMP")

######Сравнение####################

img1 = cv2.imread(os.path.abspath(orig_img_name))
img2 = cv2.imread(os.path.abspath('img_no_err.bmp'))

print(mse(img1, img2))
print(psnr(img1, img2))
psnr = cv2.PSNR(img1, img2)
print(psnr)

cv2.MSER
"""
print("Обычная ошибка")
mse = mse_diff(image, img_err)
print(mse)

psnr = psnr_diff(mse)
print(psnr)

print("Гилберт")
mse = mse_diff(image, img_err_gilbert)
print(mse)

psnr = psnr_diff(mse)
print(psnr)"""

# diff = ImageChops.difference(image_orig, image)
# diff.show()

pass
