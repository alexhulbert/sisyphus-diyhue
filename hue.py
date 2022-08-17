#!/usr/bin/env python3
import json
from flask import Flask, request
import colorsys
from math import log, pi

import thread

from neopixel import *
from colorFunctions import fill, hsbBlend
from easing import easeOut

light1 = Flask("diyhue1")
light2 = Flask("diyhue2")
light3 = Flask("diyhue3")

lights = None
on = [True, True, True]
bri = [255, 255, 255]
xy = [[0, 0], [0, 0], [0, 0]]
ct = [0, 0, 0]
hue = [0, 0, 0]
sat = [0, 0, 0]
colormode = ['xy', 'xy', 'xy']
newcolor = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
oldcolor = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
transitionstate = [1, 1, 1]
theta = 0

@light1.route('/detect', methods=['GET'])
def detectOne():
  return detect(0)
@light2.route('/detect', methods=['GET'])
def detectTwo():
  return detect(1)
@light3.route('/detect', methods=['GET'])
def detectThree():
  return detect(2)

def detect(i):
  return json.dumps({
    'name': 'Sisyphus ' + str(i + 1),
    'protocol': 'native_single',
    'modelid': 'LCT015',
    'type': 'rgbw',
    'mac': 'b8:27:eb:3d:e8:06',
    'version': 4.2
  })

@light1.route('/state', methods=['GET'])
def getStateOne():
  return getState(0)
@light2.route('/state', methods=['GET'])
def getStateTwo():
  return getState(1)
@light3.route('/state', methods=['GET'])
def getStateThree():
  return getState(2)

def getState(i):
  global on, bri, xy, ct, hue, sat, colormode
  return json.dumps({
    'on': on[i],
    'bri': bri[i],
    'xy': xy[i],
    'ct': ct[i],
    'hue': hue[i],
    'sat': sat[i],
    'colormode': colormode[i]
  })

@light1.route('/state', methods=['PUT'])
def putStateOne():
  return putState(0)
@light2.route('/state', methods=['PUT'])
def putStateTwo():
  return putState(1)
@light3.route('/state', methods=['PUT'])
def putStateThree():
  return putState(2)

def putState(i):
  global on, bri, xy, ct, hue, sat, colormode
  data = json.loads(request.data)
  if 'on' in data:
    on[i] = data['on']
  if 'bri' in data:
    bri[i] = data['bri']
  if 'xy' in data:
    xy[i] = data['xy']
    colormode[i] = 'xy'
  if 'ct' in data:
    ct[i] = data['ct']
    colormode[i] = 'ct'
  if 'hue' in data:
    hue[i] = data['hue']
    colormode[i] = 'hs'
  if 'sat' in data:
    sat[i] = data['sat']
    colormode[i] = 'hs'
  updateLight(i)
  drawLights()
  return getState(i)

def startLightOne():
  light1.run(host="0.0.0.0", port=8801, debug=True, use_reloader=False)
def startLightTwo():
  light2.run(host="0.0.0.0", port=8802, debug=True, use_reloader=False)
def startLightThree():
  light3.run(host="0.0.0.0", port=8803, debug=True, use_reloader=False)

def drawLights():
  global newcolor, lights, theta, on
  numLights = lights.numPixels() + 1
  color = [
    hsbBlend(Color(*oldcolor[0]), Color(*newcolor[0]), easeOut(transitionstate[0])) if on[0] else Color(0, 0, 0, 0),
    hsbBlend(Color(*oldcolor[1]), Color(*newcolor[1]), easeOut(transitionstate[1])) if on[1] else Color(0, 0, 0, 0),
    hsbBlend(Color(*oldcolor[2]), Color(*newcolor[2]), easeOut(transitionstate[2])) if on[2] else Color(0, 0, 0, 0)
  ]
  for n in range(numLights):
    pos = n / float(numLights)
    if 0 <= pos < (1 / 3.0):
      ratio = pos * 3
      finalColor = hsbBlend(color[0], color[1], ratio)
    elif (1 / 3.0) <= pos < (2 / 3.0):
      ratio = (pos - (1 / 3.0)) * 3
      finalColor = hsbBlend(color[1], color[2], ratio)
    elif (2 / 3.0) <= pos < 1:
      ratio = (pos - (2 / 3.0)) * 3
      finalColor = hsbBlend(color[2], color[0], ratio) 
    lights.setPixelColor(n, finalColor)

def updateLight(i):
  # oldcolor[i] = hsbBlend(oldcolor[i], newcolor[i], easeOut(transitionstate[i]))
  oldcolor[i] = newcolor[i]
  # transitionstate[i] = 0
  # start timer
  newcolor[i] = computeColor(i)
  print(newcolor[i])

def computeColor(i):
  global xy, bri, hue, sat, ct
  if colormode[i] == 'xy':
    return addWhite(convertXy(xy[i][0], xy[i][1], bri[i]))
  if colormode[i] == 'ct':
    return convertCt(ct[i], bri[i])
  if colormode[i] == 'hs':
    return addWhite(colorsys.hsv_to_rgb(hue[i] / 255.0, sat[i] / 255.0, bri[i] / 254.0))

def init(strip, tableState):
  global lights, theta
  lights = strip
  theta = tableState['theta'] / 2 / pi
  fill(strip, Color(0, 0, 0))
  thread.start_new_thread(startLightOne, ())
  thread.start_new_thread(startLightTwo, ())
  thread.start_new_thread(startLightThree, ())

def update(strip, tableState):
  global lights, theta
  theta = tableState['theta'] / 2 / pi
  # drawLights()

# import threading
# threading.Thread(target=startLightOne).start()
# threading.Thread(target=startLightTwo).start()
# threading.Thread(target=startLightThree).start()

def convertXy(X, Y, bri):
    optimal_bri = bri
    if optimal_bri < 5:
        optimal_bri = 5
    Z = 1.0 - X - Y

    # sRGB D65 conversion
    r = X * 3.2406 - Y * 1.5372 - Z * 0.4986
    g = -X * 0.9689 + Y * 1.8758 + Z * 0.0415
    b = X * 0.0557 - Y * 0.2040 + Z * 1.0570

    # Apply gamma correction
    r = (12.92 * r) if r <= 0.0031308 else ((1.0 + 0.055) * pow(r, 1.0 / 2.4) - 0.055)
    g = (12.92 * g) if g <= 0.0031308 else ((1.0 + 0.055) * pow(g, 1.0 / 2.4) - 0.055)
    b = (12.92 * b) if b <= 0.0031308 else ((1.0 + 0.055) * pow(b, 1.0 / 2.4) - 0.055)

    if r > b and r > g:
        # red is biggest
        if r > 1.0:
            g = g / r
            b = b / r
            r = 1.0
    elif g > b and g > r:
        # green is biggest
        if g > 1.0:
            r = r / g
            b = b / g
            g = 1.0
    elif b > r and b > g:
        # blue is biggest
        if b > 1.0:
            r = r / b
            g = g / b
            b = 1.0

    r = 0 if r < 0 else r
    g = 0 if g < 0 else g
    b = 0 if b < 0 else b

    return [int(r * optimal_bri), int(g * optimal_bri), int(b * optimal_bri)]

def convertCt(ct, bri):
  hectemp = 10000 / float(ct)
  r, g, b = 0, 0, 0
  if (hectemp <= 66):
    r = 255
    g = 99.4708025861 * log(hectemp) - 161.1195681661
    b = 0 if hectemp <= 19 else (138.5177312231 * log(hectemp - 10) - 305.0447927307)
  else:
    r = 329.698727446 * pow(hectemp - 60, -0.1332047592)
    g = 288.1221695283 * pow(hectemp - 60, -0.0755148492)
    b = 255
  r = 255 if r > 255 else r
  g = 255 if g > 255 else g
  b = 255 if b > 255 else b
  return [int(r * (bri / 255.0)), int(g * (bri / 255.0)), int(b * (bri / 255.0)), bri]

kWhiteRedChannel = 255
kWhiteGreenChannel = 215
kWhiteBlueChannel = 177
def addWhite(rgb):
  # These values are what the 'white' value would need to
  # be to get the corresponding color value.
  [r, g, b] = rgb
  whiteValueForRed = r * 255.0 / kWhiteRedChannel
  whiteValueForGreen = g * 255.0 / kWhiteGreenChannel
  whiteValueForBlue = b * 255.0 / kWhiteBlueChannel

  # Set the white value to the highest it can be for the given color
  # (without over saturating any channel - thus the minimum of them).
  minWhiteValue = min(whiteValueForRed,
                      min(whiteValueForGreen,
                          whiteValueForBlue))
  Wo = 255 if minWhiteValue > 255 else int(minWhiteValue)

  # The rest of the channels will just be the original value minus the
  # contribution by the white channel.
  Ro = int(r - minWhiteValue * kWhiteRedChannel / 255.0)
  Go = int(g - minWhiteValue * kWhiteGreenChannel / 255.0)
  Bo = int(b - minWhiteValue * kWhiteBlueChannel / 255.0)

  return [Ro, Go, Bo, Wo]
