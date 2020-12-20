import os
import random

import cv2
import numpy as np


def calc_block_avg(i, j, block_x, block_y, pix):
    p = block_x * block_y
    avg = 0
    avg_pow = 0
    dsp = 0
    sum = 0
    sum2 = 0

    for x in range(block_x):
        for y in range(block_y):
            sum = sum + pix[j + y][i + x][0]
            sum2 = sum2 + (pix[j + y][i + x][0] ** 2)

            # print(x, y)

    avg = sum / (block_x * block_y)
    avg_pow = (sum2 / (block_x * block_y))
    dsp = avg_pow - avg ** 2
    d = avg

    q = 0

    for x in range(block_x):
        for y in range(block_y):
            if pix[j + y][i + x][0] > avg:
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
            if pix[j + y][i + x][0] >= d:
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


def gilbert(state, err_min, err_max, do_step):
    if do_step:
        if state == 1:
            # from good to bad
            res = gamble(0.1)
            if res == 1:  # perehod v B
                state = 0

        else:
            # from bad to good
            res = gamble(0.4)
            if res == 1:  # perehod v G
                state = 1

    if state == 1:
        got_err = gamble(err_min)
    else:
        got_err = gamble(err_max)

    return state, got_err


def simple_err(data, err_chance):
    block_numb = len(data) - 2

    for blc in range(block_numb):
        cur_data = data[blc]
        code = cur_data[2]
        a = cur_data[0]
        b = cur_data[1]
        numb_code = len(code)
        numb_a = len(a)
        numb_b = len(b)

        for i in range(numb_a):
            if gamble(err_chance):
                a = err(a, i)
        for i in range(numb_b):
            if gamble(err_chance):
                b = err(b, i)
        for i in range(numb_code):
            if gamble(err_chance):
                code = err(code, i)

        data[blc][0] = a
        data[blc][1] = b
        data[blc][2] = code
    return data


def gilbert_err(data, err_min, err_max, step_range):
    block_numb = len(data) - 2
    gilbert_state = 1
    cur_step = 0
    for blc in range(block_numb):
        # print(gilbert_state)
        cur_data = data[blc]
        code = cur_data[2]
        a = cur_data[0]
        b = cur_data[1]
        numb_code = len(code)
        numb_a = len(a)
        numb_b = len(b)

        for i in range(numb_a):
            # переход 1 раз в step_range бит, ошибка каждый шаг
            if cur_step < step_range:
                gilbert_state, got_err = gilbert(gilbert_state, err_min, err_max, do_step=False)
            else:
                gilbert_state, got_err = gilbert(gilbert_state, err_min, err_max, do_step=True)
                cur_step = 0

            if got_err:
                a = err(a, i)
            cur_step = cur_step + 1

        for i in range(numb_b):
            # переход 1 раз в step_range бит, ошибка каждый шаг
            if cur_step < step_range:
                gilbert_state, got_err = gilbert(gilbert_state, err_min, err_max, do_step=False)
            else:
                gilbert_state, got_err = gilbert(gilbert_state, err_min, err_max, do_step=True)
                cur_step = 0

            if got_err:
                b = err(b, i)

        for i in range(numb_code):
            if cur_step < step_range:
                gilbert_state, got_err = gilbert(gilbert_state, err_min, err_max, do_step=False)
            else:
                gilbert_state, got_err = gilbert(gilbert_state, err_min, err_max, do_step=True)
                cur_step = 0

            if got_err:
                code = err(code, i)

        data[blc][0] = a
        data[blc][1] = b
        data[blc][2] = code
    return data


def compress_img(img, block_x, block_y):
    width = len(img[0])  # Определяем ширину.
    height = len(img)  # Определяем высоту.
    block_numb = int(round(width * height / (block_x * block_y)))

    res = []

    for blc in range(block_numb):
        # print(blc)
        i = (blc * block_x) % width
        j = int(block_y * (blc * block_x // width))

        # print(i, j)
        res.append(calc_block_avg(i, j, block_x, block_y, img))

    # additional info about size
    res.append(width)
    res.append(height)
    return res


def decompress_img(compressed_img, block_x, block_y):
    width = compressed_img[-2]
    height = compressed_img[-1]

    block_numb = int(round(width * height / (block_x * block_y)))

    blank_image = np.zeros((height, width, 3), np.uint8)
    for blc in range(block_numb):
        cur_data = compressed_img[blc]
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
                    blank_image[j + y][i + x][0] = b
                    blank_image[j + y][i + x][1] = b
                    blank_image[j + y][i + x][2] = b
                else:
                    blank_image[j + y][i + x][0] = a
                    blank_image[j + y][i + x][1] = a
                    blank_image[j + y][i + x][2] = a
                cur = cur + 1

    return blank_image


def proc_no_err(name, format, block):
    orig_img_name = name + format

    block_x = block
    block_y = block

    image = cv2.imread(PATH + "\\" + orig_img_name)

    compressed_img = compress_img(image, block_x, block_y)

    decompressed_img = decompress_img(compressed_img, block_x, block_y)

    cv2.imwrite(PATH + "\\" + name + "\\" + "no_errors_b" + str(block_x) + ".bmp", decompressed_img)
    print(" done -> " + PATH + "\\" + name + "\\" + "no_errors_b" + str(block_x) + ".bmp")


def proc_simple_err(name, format, block, err_chance):
    orig_img_name = name + format

    block_x = block
    block_y = block

    image = cv2.imread(PATH + "\\" + orig_img_name)

    compressed_img = compress_img(image, block_x, block_y)

    compressed_img_with_simple_err = simple_err(compressed_img, err_chance)

    decompressed_img = decompress_img(compressed_img_with_simple_err, block_x, block_y)

    cv2.imwrite(PATH + "\\" + name + "\\" + "simple_errors_b" + str(block_x) + ".bmp", decompressed_img)
    print(" done -> " + PATH + "\\" + name + "\\" + "simple_errors_b" + str(block_x) + ".bmp")


def proc_gilbert_err(name, format, block, err_chance_min, err_chance_max, step_range):
    orig_img_name = name + format

    block_x = block
    block_y = block

    image = cv2.imread(PATH + "\\" + orig_img_name)

    compressed_img = compress_img(image, block_x, block_y)

    compressed_img_with_simple_err = gilbert_err(compressed_img, err_chance_min, err_chance_max, step_range)

    decompressed_img = decompress_img(compressed_img_with_simple_err, block_x, block_y)

    cv2.imwrite(PATH + "\\" + name + "\\" + "gilbert_errors_b" + str(block_x) + ".bmp", decompressed_img)
    print(" done -> " + PATH + "\\" + name + "\\" + "gilbert_errors_b" + str(block_x) + ".bmp")


###############

PATH = os.path.abspath(os.getcwd())

proc_no_err("AMDTest", ".bmp", block=4)
proc_simple_err("AMDTest", ".bmp", block=4, err_chance=1 / 1000)
proc_gilbert_err("AMDTest", ".bmp", block=4, err_chance_min=1 / 100000, err_chance_max=1 / 100, step_range=1000)

proc_no_err("Gladiolus", ".bmp", block=4)
proc_simple_err("Gladiolus", ".bmp", block=4, err_chance=1 / 1000)
proc_gilbert_err("Gladiolus", ".bmp", block=4, err_chance_min=1 / 100000, err_chance_max=1 / 100, step_range=1000)

proc_no_err("Berlin", ".bmp", block=4)
proc_simple_err("Berlin", ".bmp", block=4, err_chance=1 / 1000)
proc_gilbert_err("Berlin", ".bmp", block=4, err_chance_min=1 / 100000, err_chance_max=1 / 100, step_range=1000)

# proc_no_err("Berlin", ".bmp", block=8)
# proc_simple_err("Berlin", ".bmp", block=8, err_chance=1 / 1000)
# proc_gilbert_err("Berlin", ".bmp", block=8, err_chance_min=1 / 100000, err_chance_max=1 / 100, step_range=1000)
