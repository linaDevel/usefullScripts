#!/usr/bin/python
from gi.repository import Gio

import compizconfig
import commands
import time
import re

ctx = compizconfig.Context()
bg = Gio.Settings.new("org.gnome.desktop.background")


def get_screen_count():
    core = ctx.Plugins['core']
    return int(core.Screen['hsize'].Value), int(core.Screen['vsize'].Value)


def get_screen_size():
    screen_size = re.search(
        "-geometry ([0-9]+)x([0-9]+)\+",
        commands.getoutput("xwininfo -root -stats")
    ).groups()
    return int(screen_size[0]), int(screen_size[1])


def get_screen_offset():
    screen_offset = re.search(
        "_NET_DESKTOP_VIEWPORT = ([0-9]+), ([0-9]+)\s*$",
        commands.getoutput("xprop -root -notype _NET_DESKTOP_VIEWPORT")
    ).groups()
    return int(screen_offset[0]), int(screen_offset[1])


def set_wallpaper(wallpaper):
    bg.set_string("picture-uri", "file://" + wallpaper)

if __name__ == "__main__":
    hsize, vsize = get_screen_count()

    xsize, ysize = get_screen_size()

    wpp = ctx.Plugins['wallpaper']
    cscreen = -1

    while True:
        xoff, yoff = get_screen_offset()
        x, y = xoff / xsize, yoff / ysize
        screen = x + y * hsize
        if not screen == cscreen:
            cwall = wpp.Screen['bg_image'].Value[screen]
            print cwall
            set_wallpaper(cwall)
            cscreen = screen
            thread.sleep(2)

        time.sleep(0.5)
