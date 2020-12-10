import numpy as np
from PIL import Image, ImageDraw


def image_to_grey(original_im, height, width):
    array_gray = np.zeros([height, width])
    for row in range(height):
        for col in range(width):
            r = original_im[col, row][0]
            g = original_im[col, row][1]
            b = original_im[col, row][2]
            gray = (r + g + b) // 3  # перевод в оттенки серого
            array_gray[row, col] = gray
    return array_gray


def enter(array, height, width):
    lst = []
    print("width = ", width, "height =", height)
    for row in range(height):
        for col in range(width):
            corepixel = array[row, col]
            lst.append(corepixel)
    return lst


def encode(lst):
    count = 1
    result = []
    old = lst[0]
    for num in lst[1:]:
        if num == old:
            count += 1
        else:
            result.append((old, count))
            count = 1
            old = num
    result.append((old, count))
    return result


def decode(lst, height, width):
    array_decode = np.zeros([height + 1, width + 1])
    k = len(lst)
    row = 0
    col = 0
    for pair in lst:
        bright = pair[0]
        count = pair[1]
        for x in range(0, count):
            if (col + 1 < width):
                col += 1
            else:
                col = 0
                row += 1
            array_decode[row, col] = bright
    return array_decode


# рисуем
def draw_image_to_grey(array_gray, draw, width, height):
    for row in range(0, height):
        for col in range(0, width):
            grey = array_gray[row, col]
            draw.point((col, row), (int(grey), int(grey), int(grey)))


def main():
    image = Image.open("AMDTest"".bmp")  # Открываем изображение.
    draw = ImageDraw.Draw(image)  # Создаем инструмент для рисования.
    height = image.size[1]  # Определяем ширину.
    width = image.size[0]  # Определяем высоту.
    pix = image.load()  # Выгружаем значения пикселей.

    array_gray1 = image_to_grey(pix, height, width)
    array_gray2 = enter(array_gray1, height, width)
    array_gray3 = encode(array_gray2)
    array_gray4 = decode(array_gray3, height, width)
    draw_image_to_grey(array_gray4, draw, width, height)

    image.save("compression.bmp", "bmp")
    del draw


main()
