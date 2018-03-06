import os
from PIL import Image, ImageFont, ImageDraw
import string


class ImageGenerator:
    def __init__(self, font_file, font_size, image_size, margin_left=0, margin_top=0, draw_borders=False):
        """
        :param font_file: string - путь до файла шрифта
        :param font_size: int - размер шрифта
        :param image_size: int - размер изображения с текстом
        :param margin_left: float - сдвиг слева в процентах от ширины буквы
        :param margin_top: float - сдвиг сверху в процентах от длины буквы
        :param draw_borders: bool - рисовать границы буквы
        """
        self._font_file = font_file
        self._font_size = font_size
        self._image_size = image_size
        self._margin_left = margin_left
        self._margin_top = margin_top
        self._draw_borders = draw_borders

    def to_image(self, text, image_file, text_file):
        """
        :param text: string
        :param image_file: string
        :param text_file: string - записать координаты прямоугольника с буквой в файл
        :return: None
        """
        font = ImageFont.truetype(self._font_file, self._font_size)
        width, height = font.getsize(text)

        x = (self._image_size - width) / 2
        y = (self._image_size - height) / 2

        x1 = x + self._margin_left * width
        y1 = y - self._margin_top * height
        x2 = x1 + width * (1 - self._margin_left) ** 2
        y2 = y1 + height * (1 + self._margin_top) ** 2

        image = Image.new("RGBA", (self._image_size, self._image_size), (255, 255, 255))
        draw = ImageDraw.Draw(image)

        if self._draw_borders:
            draw.rectangle(((x, y), (x + width, y + height)),
                           fill="red")
            draw.rectangle(((x1, y1), (x2, y2)),
                           fill="blue")

        draw.text((x + self._margin_left * width, y + self._margin_top * height), text, (0, 0, 0), font=font)
        image.save(image_file, format="png")

        with open(text_file, 'w') as f:
            f.write("%s %s %s %s" % (x1, y1, x2, y2))


def generate_letter_images():
    generator = ImageGenerator(font_file="fonts/Stay Wildy.ttf",
                               font_size=100,
                               image_size=100,
                               draw_borders=True)
    os.makedirs("result", exist_ok=True)
    for letter in string.ascii_lowercase:
        generator.to_image(letter, "result/%s.png" % letter, "result/%s.txt" % letter)


if __name__ == "__main__":
    generate_letter_images()
