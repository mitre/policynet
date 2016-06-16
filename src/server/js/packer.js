// Copyright (c) 2011, 2012, 2013 Jake Gordon and contributors
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.
/******************************************************************************
//
// https://github.com/jakesgordon/bin-packing
// Included here (as opposed to in bower.json) because the JS is malformatted,
// (missing ending semicolon) and cause the following script to throw error:
// "TypeError: (intermediate value)(...) is not a function"
// http://stackoverflow.com/questions/20307462/js-cant-combine-lib-files
// Alternative solution to still include this file with bower would be to
// always include this the last.
//
//
/******************************************************************************
This is a very simple binary tree based bin packing algorithm that is initialized
with a fixed width and height and will fit each block into the first node where
it fits and then split that node into 2 parts (down and right) to track the
remaining whitespace.
Best results occur when the input blocks are sorted by height, or even better
when sorted by max(width,height).
Inputs:
------
	w:       width of target rectangle
	h:      height of target rectangle
	blocks: array of any objects that have .w and .h attributes
Outputs:
-------
	marks each block that fits with a .fit attribute pointing to a
	node with .x and .y coordinates
Example:
-------
	var blocks = [
		{ w: 100, h: 100 },
		{ w: 100, h: 100 },
		{ w:  80, h:  80 },
		{ w:  80, h:  80 },
		etc
		etc
	];
	var packer = new Packer(500, 500);
	packer.fit(blocks);
	for(var n = 0 ; n < blocks.length ; n++) {
		var block = blocks[n];
		if (block.fit) {
			Draw(block.fit.x, block.fit.y, block.w, block.h);
		}
	}
******************************************************************************/

Packer = function(w, h) {
	this.init(w, h);
};

Packer.prototype = {

	init: function(w, h) {
		this.root = { x: 0, y: 0, w: w, h: h };
	},

	fit: function(blocks) {
		var n, node, block;
		for (n = 0; n < blocks.length; n++) {
			block = blocks[n];
			if (node = this.findNode(this.root, block.w, block.h))
				block.fit = this.splitNode(node, block.w, block.h);
		}
	},

	findNode: function(root, w, h) {
		if (root.used)
			return this.findNode(root.right, w, h) || this.findNode(root.down, w, h);
		else if ((w <= root.w) && (h <= root.h))
			return root;
		else
			return null;
	},

	splitNode: function(node, w, h) {
		node.used = true;
		node.down  = { x: node.x,     y: node.y + h, w: node.w,     h: node.h - h };
		node.right = { x: node.x + w, y: node.y,     w: node.w - w, h: h          };
		return node;
	}

}

module.exports = {
	Packer: Packer
};
