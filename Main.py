import random

import StringBuilder
from PIL import Image, ImageDraw  # Подключим необходимые библиотеки.

image = Image.open("1.jpg")  # Открываем изображение.
draw = ImageDraw.Draw(image)  # Создаем инструмент для рисования.
width = image.size[0]  # Определяем ширину.
height = image.size[1]  # Определяем высоту.
pix = image.load()  # Выгружаем значения пикселей.

#####Параметры#######################
chance = 1 / 100   ########Вероятность ошибки#######
block_x = 8         #########Размер блока#######
block_y = 6         ########Размер блока########
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
            if gamble(chance):
                a = err(a, i)
        for i in range(numb_b):
            if gamble(chance):
                b = err(b, i)
        for i in range(numb_code):
            if gamble(chance):
                code = err(code, i)

        data[blc][0] = a
        data[blc][1] = b
        data[blc][2] = code
    return data


######оттенки серого########
for i in range(width):
    for j in range(height):
        a = pix[i, j][0]
        b = pix[i, j][1]
        c = pix[i, j][2]
        S = (a + b + c) // 3
        draw.point((i, j), (S, S, S))

image.save("gray.jpg", "JPEG")

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
data2 = some_err(data)
######Распаковка###############
for blc in range(block_numb):
    cur_data = data2[blc]
    code = cur_data[2]
    a = cur_data[0]
    b = cur_data[1]
    #print(a)
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

image.save("res.jpg", "JPEG")
del draw

pass
