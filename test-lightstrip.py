#!/usr/bin/env python3
import json
from flask import Flask, request
# XXX: import thread

# XXX: from neopixel import *
# XXX: from colorFunctions import fill

flask = Flask("diyhue")

lights = None
on = True
bri = 254
xy = [{ 'x': 0, 'y': 0 }, { 'x': 0, 'y': 0 }, { 'x': 0, 'y': 0 }]
ct = 0
hue = 0
sat = 0
colormode = 'hs'

@flask.route('/detect', methods=['GET'])
def detect():
	return json.dumps({
		'name': 'Sisyphus',
		'protocol': 'native_single',
		'modelid': 'LCX004',
		'type': 'sk6812_gradient_lightstrip',
		'mac': 'b8:27:eb:3d:e8:06',
		'version': 4.2
	})

@flask.route('/state', methods=['GET'])
def getState():
	global on, bri, xy, ct, hue, sat, colormode
	if colormode == 'xy':
		return json.dumps({
			'on': on,
			'bri': bri,
			'colormode': colormode,
			'xy': [xy[0]['x'], xy[0]['y']]
		})
	if colormode == 'ct':
		return json.dumps({
			'on': on,
			'bri': bri,
			'colormode': colormode,
			'ct': ct
		})
	if colormode == 'hs':
		return json.dumps({
			'on': on,
			'bri': bri,
			'colormode': colormode,
			'hue': hue,
			'sat': sat
		})
	return json.dumps({
		'on': on,
		'bri': bri,
		'colormode': colormode
	})

@flask.route('/state', methods=['PUT'])
def putState():
	global on, bri, xy, ct, hue, sat, colormode
	data = json.loads(request.data)
	print(data)
	if 'on' in data:
		on = data['on']
	if 'bri' in data:
		bri = data['bri']
	if 'gradient' in data:
		xy = list(map(lambda p: p['color']['xy'], data['gradient']['points']))
		colormode = 'xy'
	if 'ct' in data:
		ct = data['ct']
		colormode = 'ct'
	if 'hue' in data:
		hue = data['hue']
		colormode = 'hs'
	if 'sat' in data:
		sat = data['sat']
		colormode = 'hs'
	return request.data

def base():
	global lights
	# XXX: fill(lights, Color(0, 0, 255, 0))

def startFlask():
	flask.run(host="0.0.0.0", port=80, debug=True, use_reloader=False)

def init(strip, table_state):
	global lights
	lights = strip
	# XXX: fill(strip, Color(0, 0, 0))
	# XXX: thread.start_new_thread(startFlask, ())

startFlask()
