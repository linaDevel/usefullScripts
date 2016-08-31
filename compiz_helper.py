from PIL import Image
import compizconfig
import pickle
import time
import os


def spiral(n):
    def spiral_part(x, y, n):
        if x == -1 and y == 0:
            return -1
        if y == (x+1) and x < (n // 2):
            return spiral_part(x-1, y-1, n-1) + 4*(n-y)
        if x < (n-y) and y <= x:
            return spiral_part(y-1, y, n) + (x-y) + 1
        if x >= (n-y) and y <= x:
            return spiral_part(x, y-1, n) + 1
        if x >= (n-y) and y > x:
            return spiral_part(x+1, y, n) + 1
        if x < (n-y) and y > x:
            return spiral_part(x, y-1, n) - 1

    array = [[0] * n for j in xrange(n)]
    for x in xrange(n):
        for y in xrange(n):
            array[x][y] = spiral_part(y, x, n)
    return array


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
        if os.path.exists("%s.bness" % file):
            return ImageBrightness(
                file, pickle.loads(
                    open("%s.bness" % file, 'r').read()
                )
            )
        else:
            image = Image.open(file)
            image = image.convert("L")
            w, h = image.size
            summ = 0
            for x in range(w):
                for y in range(h):
                    summ += image.getpixel((x, y))
            open("%s.bness" % file, 'w').write(pickle.dumps(
                float(summ) / (w * h)
            ))

            return ImageBrightness(file, float(summ) / (w * h))

    def order_wallapapers_by_brightness(self, files, reverse=False):
        wallpapers = []
        for file_path in files:
            if os.path.isfile(file_path):
                if os.path.splitext(file_path)[1].lower() in ['.jpg', '.png']:
                    wallpapers.append(self.calculate_brightness(file_path))
        wallpapers.sort(reverse=reverse)
        return wallpapers

    def set_wallpapers_from_folder_ordered(self, path, reverse=False):
        wallpapers = []
        if os.path.exists(path) and os.path.isdir(path):
            wallpapers = self.order_wallapapers_by_brightness(            
                os.listdir(path), reverse
            )
           
        self.set_wallpapers_from_array(
            [wallpaper.file for wallpaper in wallpapers]
        )
        return wallpapers

    def list_wallpapers(self):
        screen = self.context.Plugins['wallpaper'].Screen
        return screen['bg_image'].Value

    def sort_wallpapers(self, reverse=False):
        wallpapers = self.order_wallapapers_by_brightness(
            self.list_wallpapers(), reverse=reverse
        )
        self.set_wallpapers_from_array(
            [wallpaper.file for wallpaper in wallpapers]
        )
        return wallpapers

    def spiral_wallpapers(self, reverse=False, left=False, top=False):
        wallpapers = self.order_wallapapers_by_brightness(
            self.list_wallpapers(), reverse=reverse
        )

        import math
        n = int(math.sqrt(len(wallpapers)))

        order = spiral(n)
        print order

        ordered = []
        for y in (range(0, n) if top else range(n - 1, -1, -1)):
            for x in (range(0, n) if left else range(n - 1, -1, -1)):
                ordered.append(wallpapers[order[y][x]])

        self.set_wallpapers_from_array(
            [wallpaper.file for wallpaper in ordered]
        )
        return ordered

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
    parser.add_argument(
        '-l', '--left',
        action="store_true", help="Order image left or right spiral"
    )
    parser.add_argument(
        '-t', '--top',
        action="store_true", help="Order image top or bottom spiral"
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
    elif args.action == "spiral":
        print "Sorting wallpapers"
        for wallpaper in ch.spiral_wallpapers(
            args.reverse, args.left, args.top
        ):
            print "\t%s" % wallpaper
    else:
        print "Unknown action '%s'" % args.action

    ch.commit()
    time.sleep(0.5)
