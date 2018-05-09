from PIL import Image, ImageDraw
import numpy as np
import cv2


class FontLibException(Exception):
    pass


class DimensionError(FontLibException):
    pass


class ArgumentError(FontLibException):
    pass


class Rect:
    def __init__(self, x0, y0, x1, y1, x2, y2, x3, y3):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.x3 = x3
        self.y3 = y3

    def __repr__(self):
        return "{x0: %s, y0: %s, x1: %s, y1: %s, x2: %s, y2: %s, x3: %s, y3: %s}" % \
               (self.x0, self.y0, self.x1, self.y1, self.x2, self.y2, self.x3, self.y3)


class Char:
    def __init__(self, char, font_size, image, char_rect, font_color):
        """
        :param char: str
        :param font_size: int
        :param image: Image
        :param char_rect: Rect
        :param font_color: (b, g, r)
        """
        self.char = char
        self.font_size = font_size
        self.image = image
        self.rect = char_rect
        self.font_color = font_color

    def add_background(self, bg_img):
        """
        :param bg_img: PIL.Image.Image - изображение с фоном
        :return: Char
        """
        result = Image.new("RGBA", (self.image.size[0], self.image.size[1]))
        result.paste(bg_img, (0, 0))
        result.paste(self.image, (0, 0), self.image)
        return Char(self.char, self.font_size, result, self.rect, self.font_color)

    def blur(self, kernel):
        """
        :param kernel: (x, y)
        :return: Char
        """
        image = Image.fromarray(cv2.blur(np.array(self.image), kernel))
        return Char(self.char, self.font_size, image, self.rect, self.font_color)

    def apply_homography(self, dst_rect):
        """
        Применить гомографию.
        :param dst_rect: Rect - прямоугольник, в который должна перейти буква
        :return Char
        """
        src_points = np.array([[self.rect.x0, self.rect.y0],
                               [self.rect.x1, self.rect.y1],
                               [self.rect.x2, self.rect.y2],
                               [self.rect.x3, self.rect.y3]])

        dst_points = np.array([[dst_rect.x0, dst_rect.y0],
                               [dst_rect.x1, dst_rect.y1],
                               [dst_rect.x2, dst_rect.y2],
                               [dst_rect.x3, dst_rect.y3]])

        image = np.array(self.image)
        h, status = cv2.findHomography(src_points, dst_points)
        img_dst = cv2.warpPerspective(image, h, (image.shape[0], image.shape[1]))

        rect_dst = Rect(*dst_points.flatten())
        return Char(self.char, self.font_size, Image.fromarray(img_dst), rect_dst, self.font_color)

    @staticmethod
    def from_font(char, font, image_size, font_color=None, font_texture=None):
        """
        :param char: string - буква
        :param font: PIL.ImageFont.FreeTypeFont - шрифт
        :param image_size: (width, height) - размер изображения
        :param font_color: (b, g, r) - цвет фона
        :param font_texture: PIL.Image.Image - изображение для текстуры шрифта
        :return: Сhar
        """
        if font_color is None and font_texture is None:
            raise ArgumentError("One of these must be provided: font_color, font_texture")

        width, height = font.getsize(char)
        bg_color = (255, 255, 255, 0)

        x = (image_size[0] - width) / 2
        y = (image_size[1] - height) / 2

        image = Image.new("RGBA", (image_size[0], image_size[1]), bg_color)
        draw = ImageDraw.Draw(image)

        draw.text((x, y), char, font_color, font=font)

        image = np.array(image)

        if font_texture is not None:
            if font_texture.size[0] < image.shape[0] or font_texture.size[1] < image.shape[1]:
                raise DimensionError("texture image must have at least the same dimensions as image_size")

            font_texture = np.array(font_texture)
            font_texture = font_texture[:image.shape[0], :image.shape[1]] # crop to match image_size

            if font_texture.shape[2] == 3: # needs alpha channel
                font_texture = cv2.cvtColor(font_texture, cv2.COLOR_RGB2RGBA)

            cv2.imwrite("tex.png", font_texture)

            for i in range(image.shape[0]):
                for j in range(image.shape[1]):
                    if all(image[i][j] == bg_color):
                        font_texture[i][j] = bg_color

            image = font_texture

        y_idx, x_idx, _ = np.where(np.not_equal(image, bg_color))
        x0 = np.min(x_idx)
        x1 = np.max(x_idx)
        y0 = np.min(y_idx)
        y1 = np.max(y_idx)

        image = Image.fromarray(image)

        return Char(char, font.size, image,  Rect(x0, y0, x1, y0, x0, y1, x1, y1), font_color)


