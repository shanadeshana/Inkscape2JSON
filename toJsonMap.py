#!/usr/bin/env python

import inkex
import simplepath
import json


def asInt(val):
	return int(round(float(val)))


class SplitIt(inkex.Effect):
	def __init__(self):
		inkex.Effect.__init__(self)
		self.OptionParser.add_option("--key",
						action="store",
						dest="key", default=False,
						help="use id as key")
		self.OptionParser.add_option("--size",
						action="store",
						dest="size", default=False,
						help="set size of object")

	def getCCFromGroup(self, node):
		minx = None
		miny = None
		maxx = None
		maxy = None
		for child in node:

			attributes = child.attrib

			if not 'x' in attributes or not 'y' in attributes:
				cc = self.getCC(child)
				x = cc['x']
				y = cc['y']
			else:
				x = asInt(attributes['x'])
				y = asInt(attributes['y'])

			if minx is None or x < minx:
				minx = x

			if miny is None or y < miny:
				miny = y

			if maxx is None or x > maxx:
				maxx = x

			if maxy is None or y > maxy:
				maxy = y

		if self.options.size:
			return {
				'x': minx, 'y': miny,
				'width': maxx - minx, 'height': maxy - miny
			}
		else:
			return {'x': minx, 'y': miny}

	def getCCFromPath(self, node):
		minx = None
		miny = None
		maxx = None
		maxy = None
		paths = simplepath.parsePath(node.get('d'))

		for path in paths:

			if path[0] in ('a', 'A'):

				x = path[1][-2]
				y = path[1][-1]

			else:
				for i in range(0, len(path[1]), 2):
					x = asInt(path[1][i])
					y = asInt(path[1][i + 1])

			if minx is None or x < minx:
				minx = x

			if miny is None or y < miny:
				miny = y

			if maxx is None or x > maxx:
				maxx = x

			if maxy is None or y > maxy:
				maxy = y
		if self.options.size:
			return {
				'x': minx, 'y': miny,
				'width': maxx - minx, 'height': maxy - miny
			}
		else:
			return {'x': minx, 'y': miny}

	def getCC(self, node):
		cc = {'x': 0, 'y': 0}
		if node.tag == inkex.addNS('g', 'svg'):
			cc = self.getCCFromGroup(node)
		elif node.tag == inkex.addNS('path', 'svg'):
			cc = self.getCCFromPath(node)
		elif 'x' in node.attrib and 'y' in node.attrib:
			cc['x'] = asInt(node.get('x'))
			cc['y'] = asInt(node.get('y'))

		if self.options.size and \
				'width' in node.attrib and 'height' in node.attrib:
			cc['width'] = asInt(node.get('width'))
			cc['height'] = asInt(node.get('height'))

		for child in node.iter():
			if child.tag == inkex.addNS('desc', 'svg'):
				cc['param'] = child.text
				break

		return cc

	def effect(self):
		self.options.size = self.options.size.lower() == 'true'
		self.options.key = self.options.key.lower() == 'true'

		nodes = None
		if len(self.selected.keys()) > 0:
			nodes = self.selected.values()
		else:
			path = "./svg:g/*[@id]"
			nodes = self.document.iterfind(path, namespaces=inkex.NSS)

		if self.options.key:
			elems = {}
			for node in nodes:
				elems[node.get('id')] = self.getCC(node)
		else:
			elems = []
			for node in nodes:
				elems.append(self.getCC(node))

		inkex.errormsg(json.dumps(elems))

if __name__ == '__main__':
	e = SplitIt()
	e.affect()
