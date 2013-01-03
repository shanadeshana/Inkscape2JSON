#!/usr/bin/env python 

import inkex, simplepath
import sys, os
import json

def asInt(val):
	return int(round(float(val)))

class SplitIt(inkex.Effect):
	def __init__(self):
		inkex.Effect.__init__(self)
		self.OptionParser.add_option("--key",
						action="store",
						dest="key", default=True,
						help="use id as key")

	def getCCFromGroup(self, node):
		minx = None;
		miny = None;
		for child in node:
			
			attributes = child.attrib
			
			if not attributes.has_key('x') or not attributes.has_key('y'):
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
		return {'x': minx, 'y': miny}
	
	def getCCFromPath(self, node):
		minx = None
		miny = None
		paths = simplepath.parsePath(node.get('d'))
		
		for path in paths:
			
			if path[0] in ('a', 'A'):
				
				x = path[1][-2]
				y = path[1][-1]
				
				if minx is None or x < minx:
					minx = x
				
				if miny is None or y < miny:
					miny = y
			else:
				
				for i in range(0, len(path[1]), 2):
					x = asInt(path[1][i])
					y = asInt(path[1][i+1])
					
					if minx is None or x < minx:
						minx = x
					
					if miny is None or y < miny:
						miny = y
		return {'x': minx, 'y': miny}
	
	def getCC(self, node):
		cc = {'x': 0, 'y': 0}
		if node.tag == inkex.addNS('g','svg'):
			cc = self.getCCFromGroup(node)
		elif node.tag == inkex.addNS('path','svg'):
			cc = self.getCCFromPath(node)
		elif not node.attrib.has_key('x') or not node.attrib.has_key('y'):
			cc = node.attrib
		else:
			cc['x'] = asInt(node.get('x'))
			cc['y'] = asInt(node.get('y'))
		
		for child in node.iter():
			if child.tag == inkex.addNS('desc','svg'):
				cc['param'] = child.text
				break
		
		return cc
	
	def effect(self):
		nodes = None
		if len(self.selected.keys()) > 0:
			nodes = self.selected.values()
		else:
			path = "./svg:g/*[@id]"
			nodes = self.document.iterfind(path, namespaces=inkex.NSS)

		if self.options.key == 'true':
			elems = {};
			path = "/svg:svg/svg:g/*[@id]"
			for node in nodes:
				elems[node.get('id')] = self.getCC(node)
		else:
			elems = [];
			path = "/svg:svg/svg:g/*[@id]"
			for node in nodes:
				elems.append(self.getCC(node))
		
		inkex.errormsg(json.dumps(elems))

if __name__ == '__main__':
	e = SplitIt()
	e.affect()