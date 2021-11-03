try:
    from rgbmatrix import graphics
except ImportError:
    from RGBMatrixEmulator import graphics

import os.path

FONTNAME_DEFAULT = "4x6"
FONTNAME_KEY = "font_name"


class Layout:
    def __init__(self, layout_json, width, height):
        self.json = layout_json
        self.width = width
        self.height = height
        self.state = None
        self.default_font_name = FONTNAME_DEFAULT
        self.default_font_name = self.coords("defaults.font_name")

        self.font_cache = {}
        default_font = self.__load_font(self.default_font_name)
        self.font_cache = {self.default_font_name: default_font}

    # Returns a dictionary with "font" and "size"
    def font(self, keypath):
        d = self.coords(keypath)
        try:
            return self.__get_font_object(d[FONTNAME_KEY])
        except KeyboardInterrupt as e:
            raise e
        except:
            return self.__get_font_object(self.default_font_name)

    def coords(self, keypath):
        try:
            d = self.__find_at_keypath(keypath)
        except KeyError as e:
            raise e
        return d

    def __find_at_keypath(self, keypath):
        keys = keypath.split(".")
        rv = self.json
        for key in keys:
            rv = rv[key]
        return rv

    def __load_font(self, font_name):
        if font_name in self.font_cache:
            return self.font_cache[font_name]

        font_paths = ["assets", "submodules/matrix/fonts"]
        for font_path in font_paths:
            path = f"{font_path}/{font_name}.bdf"
            if os.path.isfile(path):
                font = graphics.Font()
                font.LoadFont(path)
                self.font_cache[font_name] = font
                return font

    def __parse_font_size(self, font_name):
        if font_name[-1] == "B":
            font_name = font_name[:-1]
        dimensions = font_name.split("x")
        return {"width": int(dimensions[0]), "height": int(dimensions[1])}

    def __get_font_object(self, font_name):
        f = self.__load_font(font_name)
        s = self.__parse_font_size(font_name)
        return {"font": f, "size": s}
