from PIL import Image
import compizconfig
import time
import os


class ImageBrightness:

    def __init__(self, file, brightness):
        self.file = file
        self.brightness = brightness

    def __cmp__(self, target):
        return cmp(self.brightness, target.brightness)

    def __str__(self):
        return "%3.5f %s" % (self.brightness, self.file)


class CompizHelper():

    def __init__(self):
        self.context = compizconfig.Context()

    def set_wallpapers_from_array(self, wallpapers):
        screen = self.context.Plugins['wallpaper'].Screen
        screen['bg_color2'].Value = [[0, 0, 0, 65535]] * len(wallpapers)
        screen['bg_color1'].Value = [[0, 0, 0, 65535]] * len(wallpapers)
        screen['bg_image'].Value = wallpapers
        screen['bg_image_pos'].Value = [0] * len(wallpapers)
        screen['bg_fill_type'].Value = [0] * len(wallpapers)

    def set_wallpapers_from_folder(self, path, reverse=False):
        wallpapers = []
        if os.path.exists(path) and os.path.isdir(path):
            for file in os.listdir(path):
                abs_path = os.path.abspath(os.path.join(path, file))
                if os.path.isfile(abs_path):
                    if os.path.splitext(file)[1].lower() in ['.jpg', '.png']:
                        wallpapers.append(abs_path)
        wallpapers.sort(reverse=reverse)
        self.set_wallpapers_from_array(wallpapers)
        return wallpapers

    def calculate_brightness(self, file):
        image = Image.open(file)
        image = image.convert("L")
        w, h = image.size
        summ = 0
        for x in range(w):
            for y in range(h):
                summ += image.getpixel((x, y))
        return ImageBrightness(file, float(summ) / (w * h))

    def set_wallpapers_from_folder_ordered(self, path, reverse=False):
        wallpapers = []
        if os.path.exists(path) and os.path.isdir(path):
            for file in os.listdir(path):
                abs_path = os.path.abspath(os.path.join(path, file))
                if os.path.isfile(abs_path):
                    if os.path.splitext(file)[1].lower() in ['.jpg', '.png']:
                        wallpapers.append(self.calculate_brightness(abs_path))
        wallpapers.sort(reverse=reverse)
        self.set_wallpapers_from_array(
            [wallpaper.file for wallpaper in wallpapers]
        )
        return wallpapers

    def list_wallpapers(self):
        screen = self.context.Plugins['wallpaper'].Screen
        return screen['bg_image'].Value

    def sort_wallpapers(self, reverse=False):
        wallpapers = []
        for file_path in self.list_wallpapers():
            if os.path.isfile(file_path):
                if os.path.splitext(file_path)[1].lower() in ['.jpg', '.png']:
                    wallpapers.append(self.calculate_brightness(file_path))
        wallpapers.sort(reverse=reverse)
        self.set_wallpapers_from_array(
            [wallpaper.file for wallpaper in wallpapers]
        )
        return wallpapers

    def commit(self):
        self.context.Write()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='CompizConfig helper')
    parser.add_argument(
        'action',
        type=str,
        help="Action to execute. Available actions: set, order_set, sort"
    )
    parser.add_argument('path', type=str, help="Path to directory with images")
    parser.add_argument(
        '-r', '--reverse',
        action="store_true", help="Order image directly or reverse ordered"
    )

    args = parser.parse_args()

    ch = CompizHelper()

    if args.action == "set":
        print "New wallpaper set:"
        for wallpaper in ch.set_wallpapers_from_folder(
            args.path, args.reverse
        ):
            print "\t%s" % wallpaper
    elif args.action == "order_set":
        print "New wallpaper set:"
        for wallpaper in ch.set_wallpapers_from_folder_ordered(
            args.path, args.reverse
        ):
            print "\t%s" % wallpaper
    elif args.action == "sort":
        print "Sorting wallpapers"
        for wallpaper in ch.sort_wallpapers(args.reverse):
            print "\t%s" % wallpaper
    else:
        print "Unknown action '%s'" % args.action

    ch.commit()
    time.sleep(0.5)
