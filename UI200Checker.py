# -*- coding: utf-8 -*-
"""
Created on Mon Apr 25 11:56:31 2022

@author: lkappel
"""

from ctypes import windll, Structure, c_long, byref
from PIL import ImageGrab

Item_InputBox = (182,81)
Item_ErrorBounds = (441,73, 526,88)

class POINT(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]

def queryMousePosition():
    pt = POINT()
    windll.user32.GetCursorPos(byref(pt))
    return { "x": pt.x, "y": pt.y}

def takeScreenshot(bounds=0):
    if bounds==0:
        return ImageGrab.grab()
    else:
        return ImageGrab.grab(*bounds)

a= ((1,3,4,5),(37,513,1,3))
b = (1,2,3,4)
c = (5,6,7,8)

for x in a:
    print(*x)