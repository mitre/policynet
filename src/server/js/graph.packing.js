var Packer			= require("./packer.js"),
	_				= require("lodash"),
	utils			= require("./utils.js");



// https://github.com/geidav/ombb-rotating-calipers
var Vector = function(x, y) {
	this.x = x;
	this.y = y;

	this.min = function(vec) {
		x = Math.min(x, vec.x);
		y = Math.min(y, vec.y);
	};

	this.max = function(vec) {
		x = Math.max(x, vec.x);
		y = Math.max(y, vec.y);
	};

	this.midpoint = function(vec) {
		return new Vector((x+vec.x)*0.5, (y+vec.y)*0.5);
	};

	this.clone = function() {
		return new Vector(this.x, this.y);
	};

	this.normalize = function() {
		var len = this.length();
		this.x /= len;
		this.y /= len;
	};

	this.normalized = function() {
		var vec = new Vector(this.x, this.y);
		vec.normalize();
		return vec;
	};

	this.negate = function() {
		this.x = -this.x;
		this.y = -this.y;
	};

	this.sqrLength = function() {
		return this.x * this.x + this.y * this.y;
	};

	this.length = function() {
		return Math.sqrt(this.x * this.x + this.y * this.y);
	};

	this.scale = function(len) {
		this.x *= len;
		this.y *= len;
	};

	this.add = function(vec) {
		this.x += vec.x;
		this.y += vec.y;
	};

	this.sub = function(vec) {
		this.x -= vec.x;
		this.y -= vec.y;
	};

	this.diff = function(vec) {
		return new Vector(this.x-vec.x, this.y-vec.y);
	};

	this.distance = function(vec) {
		var x = this.x-vec.x;
		var y = this.y-vec.y;
		return Math.sqrt(x*x+y*y);
	};

	this.dot = function(vec) {
		return this.x*vec.x+this.y*vec.y;
	};

	this.equals = function(vec) {
		return this.x === vec.x && this.y === vec.y;
	};

	this.orthogonal = function() {
		return new Vector(this.y, -this.x);
	};

	this.distanceToLine = function(v0, v1) {
		var sqrLen = v1.diff(v0).sqrLength();
		var u = ((this.x-v0.x)*(v1.x-v0.x)+(this.y-v0.y)*(v1.y-v0.y))/sqrLen;
		var v1c = v1.diff(v0);
		v1c.scale(u);
		var pl = v0.clone();
		pl.add(v1c);
		return this.distance(pl);
	};
};
var getSideOfLine = function(lineStart, lineEnd, point) {
	var ON = 0;
	var LEFT = 1;
	var RIGHT = 2;
	var ALMOST_ZERO = 0.00001;
	var d = (lineEnd.x-lineStart.x)*(point.y-lineStart.y)-(lineEnd.y-lineStart.y)*(point.x-lineStart.x);
	return (d > ALMOST_ZERO ? LEFT : (d < -ALMOST_ZERO ? RIGHT : ON));
};
var calcConvexHull = function(points) {
	var ON = 0;
	var LEFT = 1;
	// var RIGHT = 2;
	var ALMOST_ZERO = 0.00001;

	if (points.length < 3){
		return points;
	}


	var hullPt = points[0];
	var convexHull = [];

	for (var i=1; i<points.length; i++) {

		if (points[i].x < hullPt.x){
			hullPt = points[i];
		} else if (Math.abs(points[i].x-hullPt.x) < ALMOST_ZERO){
			if (points[i].y < hullPt.y){
				hullPt = points[i];
			}
		}
	}

	var endPt = points[0];
	do {
		convexHull.unshift(hullPt.clone());
		endPt = points[0];

		for (var j=1; j<points.length; j++) {
			var side = getSideOfLine(hullPt, endPt, points[j]);


			if (endPt.equals(hullPt) || (side === LEFT || (side === ON && hullPt.distance(points[j]) > hullPt.distance(endPt)))){
				endPt = points[j];
			}
		}

		hullPt = endPt;
	}
	while (!endPt.equals(convexHull[convexHull.length-1]));

	return convexHull;
};
var intersectLines = function(start0, dir0, start1, dir1) {
	var dd = dir0.x*dir1.y-dir0.y*dir1.x;

	var dx = start1.x-start0.x;
	var dy = start1.y-start0.y;
	var t = (dx*dir1.y-dy*dir1.x)/dd;
	return new Vector(start0.x+t*dir0.x, start0.y+t*dir0.y);
};
var calcOmbb = function(convexHull) {
	function updateOmbb(leftStart, leftDir, rightStart, rightDir, topStart, topDir, bottomStart, bottomDir) {
		var obbUpperLeft = intersectLines(leftStart, leftDir, topStart, topDir);
		var obbUpperRight = intersectLines(rightStart, rightDir, topStart, topDir);
		var obbBottomLeft = intersectLines(bottomStart, bottomDir, leftStart, leftDir);
		var obbBottomRight = intersectLines(bottomStart, bottomDir, rightStart, rightDir);
		var distLeftRight = obbUpperLeft.distance(obbUpperRight);
		var distTopBottom = obbUpperLeft.distance(obbBottomLeft);
		var obbArea = distLeftRight*distTopBottom;

		if (obbArea < BestObbArea) {
			BestObbArea = obbArea;
			BestObb = [obbUpperLeft, obbBottomLeft, obbBottomRight, obbUpperRight];
		}
	}


	var BestObbArea = Number.MAX_VALUE;
	var BestObb = [];


	var edgeDirs = [];
	var i;
	for (i=0; i<convexHull.length; i++) {
		edgeDirs.push(convexHull[(i+1)%convexHull.length].diff(convexHull[i]));
		edgeDirs[i].normalize();
	}


	var minPt = new Vector(Number.MAX_VALUE, Number.MAX_VALUE);
	var maxPt = new Vector(-Number.MAX_VALUE, -Number.MAX_VALUE);
	var leftIdx, rightIdx, topIdx, bottomIdx;

	for (i=0; i<convexHull.length; i++) {
		var pt = convexHull[i];

		if (pt.x < minPt.x) {
			minPt.x = pt.x;
			leftIdx = i;
		}

		if (pt.x > maxPt.x) {
			maxPt.x = pt.x;
			rightIdx = i;
		}

		if (pt.y < minPt.y) {
			minPt.y = pt.y;
			bottomIdx = i;
		}

		if (pt.y > maxPt.y) {
			maxPt.y = pt.y;
			topIdx = i;
		}
	}

	var leftDir = new Vector(0.0, -1);
	var rightDir = new Vector(0, 1);
	var topDir = new Vector(-1, 0);
	var bottomDir = new Vector(1, 0);

	for (i=0; i<convexHull.length; i++) {

		var phis =
		[
		Math.acos(leftDir.dot(edgeDirs[leftIdx])),
		Math.acos(rightDir.dot(edgeDirs[rightIdx])),
		Math.acos(topDir.dot(edgeDirs[topIdx])),
		Math.acos(bottomDir.dot(edgeDirs[bottomIdx])),
		];

		var lineWithSmallestAngle = phis.indexOf(Math.min.apply(Math, phis));
		switch (lineWithSmallestAngle) {
			case 0:
			leftDir = edgeDirs[leftIdx].clone();
			rightDir = leftDir.clone();
			rightDir.negate();
			topDir = leftDir.orthogonal();
			bottomDir = topDir.clone();
			bottomDir.negate();
			leftIdx = (leftIdx+1)%convexHull.length;
			break;
			case 1:
			rightDir = edgeDirs[rightIdx].clone();
			leftDir = rightDir.clone();
			leftDir.negate();
			topDir = leftDir.orthogonal();
			bottomDir = topDir.clone();
			bottomDir.negate();
			rightIdx = (rightIdx+1)%convexHull.length;
			break;
			case 2:
			topDir = edgeDirs[topIdx].clone();
			bottomDir = topDir.clone();
			bottomDir.negate();
			leftDir = bottomDir.orthogonal();
			rightDir = leftDir.clone();
			rightDir.negate();
			topIdx = (topIdx+1)%convexHull.length;
			break;
			case 3:
			bottomDir = edgeDirs[bottomIdx].clone();
			topDir = bottomDir.clone();
			topDir.negate();
			leftDir = bottomDir.orthogonal();
			rightDir = leftDir.clone();
			rightDir.negate();
			bottomIdx = (bottomIdx+1)%convexHull.length;
			break;
		}

		updateOmbb(convexHull[leftIdx], leftDir, convexHull[rightIdx], rightDir, convexHull[topIdx], topDir, convexHull[bottomIdx], bottomDir);
	}


	var orientation, height, width, rad, ref;

	if (BestObb[0].distance(BestObb[1]) > BestObb[0].distance(BestObb[3])) {
		orientation = 'clockwise';
		height = BestObb[0].distance(BestObb[3]);
		width = BestObb[0].distance(BestObb[1]);
		rad = Math.asin( (BestObb[0].y - BestObb[1].y) / width);
		ref = [BestObb[0].x, BestObb[0].y];

	} else {
		orientation = 'counterclockwise';
		height = BestObb[0].distance(BestObb[1]);
		width = BestObb[0].distance(BestObb[3]);
		rad = -Math.asin( (BestObb[2].y - BestObb[1].y) / width);
		ref = [BestObb[1].x, BestObb[1].y];

	}

	return {bestobb: BestObb,
		h: height,
		w: width,
		rad: rad,
		ori: orientation,
		ref: ref,
		dist01: BestObb[0].distance(BestObb[1]),
		dist03: BestObb[0].distance(BestObb[3])
	};
};
var clusterPacking = function(graphdata){
	var points,
		pid,
		nodeMap = {},
		node,
		convexhull,
		newCord,
		o1,
		o2,
		p,
		rad,
		packer,
		edgeLength,
		node1,
		node2,
		totalArea,
		scale = 1,
		widthScale = 2.5,
		scaleExp = 1.5,
		max_size = 0,
		margin = 0.1,
		cornerNodes = [],
		// cornerEdges = [],
		cluster_rectangle = [];


		graphdata.nodes.forEach(function(e,i){
			nodeMap[e.id.toString()] = i;
		});
	for (var i = 0; i < graphdata.clusters.length; i++){
		points = [];
		edgeLength = {};
		for (var j = 0; j < graphdata.clusters[i].length; j++){
			pid = graphdata.clusters[i][j];
			node = graphdata.nodes[nodeMap[pid]];
			points.push(new Vector(node.x, node.y));
			node.edges.forEach(function(e){
				node1 = graphdata.edges[e.edge-1].source;
				node2 = graphdata.edges[e.edge-1].target;

				if (parseInt(node1) > parseInt(node2)){
					node1 = [node2, node2 = node1][0];
				}
				if (node1!== node2 && !edgeLength[node1+"_"+node2]){
					node1_x = graphdata.nodes[nodeMap[node1]].x;
					node1_y = graphdata.nodes[nodeMap[node1]].y;
					node2_x = graphdata.nodes[nodeMap[node2]].x;
					node2_y = graphdata.nodes[nodeMap[node2]].y;

					edgeLength[node1+"_"+node2] = Math.sqrt(Math.pow(node2_x - node1_x,2) + Math.pow(node2_y - node1_y,2));
				}
			})
		}

		if (graphdata.clusters[i].length > 2){

			convexhull = calcConvexHull(points);
			cluster_rectangle[i] = calcOmbb(convexhull);
			cluster_rectangle[i].i = i;
			cluster_rectangle[i].totalUniqueEdge = _.values(edgeLength).length;
			cluster_rectangle[i].totalEdgeDistance = _.reduce(_.values(edgeLength), function(total, n) {
				return total + n;
			});
			cluster_rectangle[i].avgEdgeDistance = cluster_rectangle[i].totalEdgeDistance / cluster_rectangle[i].totalUniqueEdge;
			cluster_rectangle[i].minEdgeDistance = cluster_rectangle[i].totalEdgeDistance = _.reduce(_.values(edgeLength), function(min, n) {
				return Math.min(min, n);
			});
			max_size = max_size < Math.max(cluster_rectangle[i].w, cluster_rectangle[i].h) ? Math.max(cluster_rectangle[i].w, cluster_rectangle[i].h) : max_size;
		} else if (graphdata.clusters[i].length === 2) {

			var width = points[0].distance(points[1]);
			rad = Math.asin( (points[0].y - points[1].y) / width);
			rad = points[0].x > points[1].x ? Math.PI - rad : rad;
			var orientation = rad < 0 ? "clockwise" : "counterclockwise";
			cluster_rectangle[i] = {h: 0,
				w: width ,
				i: i,
				rad: rad,
				ori: orientation,
				ref: [points[0].x, points[0].y],
				totalUniqueEdge: _.values(edgeLength).length,
				totalEdgeDistance: _.values(edgeLength)[0],
				avgEdgeDistance: _.values(edgeLength)[0],
				minEdgeDistance: _.values(edgeLength)[0]
			};
			max_size = max_size < Math.max(cluster_rectangle[i].w, cluster_rectangle[i].h) ? Math.max(cluster_rectangle[i].w, cluster_rectangle[i].h) : max_size;

		} else {
			cluster_rectangle[i] = {
				w: 0,
				h: 0,
				i: i,
				rad: 0,
				orientation: "clockwise",
				ref: [points[0].x, points[0].y],
				totalUniqueEdge: 0,
				totalEdgeDistance: 0,
				avgEdgeDistance: 0,
				minEdgeDistance: 0
			};
		}
	}
	margin = Math.max(margin * max_size, 1);
	cluster_rectangle.forEach(function(e){
		e.scale = e.avgEdgeDistance === 0 ? 1 : Math.pow(cluster_rectangle[0].avgEdgeDistance / e.avgEdgeDistance, scaleExp);
		e.w = e.w * e.scale + margin;
		e.h = e.h * e.scale + margin;
	});
	cluster_rectangle.sort(function(a,b){return (b.w - a.w);});
	totalArea = _.reduce(cluster_rectangle, function(total, r){
		return total + r.w * r.h;
	},0)
	packer = new Packer.Packer(cluster_rectangle[0].w * widthScale, 20 * totalArea / (cluster_rectangle[0].w * widthScale));

	packer.fit(cluster_rectangle);
	cluster_rectangle.forEach(function(e,i){
		o1 = e.ref;
		o2 = [e.fit.x, e.fit.y];
		rad = e.rad;

		graphdata.clusters[e.i].forEach(function(c){
			p = [graphdata.nodes[nodeMap[c]].x, graphdata.nodes[nodeMap[c]].y];
			newCord = transform(o1,o2,p,rad,e.scale,margin / 2);
			graphdata.nodes[nodeMap[c]].x = newCord[0];
			graphdata.nodes[nodeMap[c]].y = newCord[1];
		});

		cornerNodes = [ cornerNode(e.fit.x,e.fit.y,10000000+i*10000+1,1),
		cornerNode(e.fit.x+e.w,e.fit.y,10000000+i*10000+2,2),
		cornerNode(e.fit.x+e.w,e.fit.y+e.h,10000000+i*10000+3,3),
		cornerNode(e.fit.x,e.fit.y+e.h,10000000+i*10000+4,4)];
		cornerNodes.forEach(function(e){graphdata.nodes.push(e);});
	});
	graphdata.layout = {};
	graphdata.layout.overallX = _.reduce(graphdata.nodes, function(max, n){
		return Math.max(max, n.x);
	},0);
	graphdata.layout.overallY = _.reduce(graphdata.nodes, function(max, n){
		return Math.max(max, n.y);
	},0);
	return graphdata;
}

function transform(o1,o2,p,rad,scale,margin){
	return [(Math.cos(rad) * (p[0]-o1[0]) - Math.sin(rad) * (p[1]-o1[1])) * scale + o2[0] + margin,
			(Math.sin(rad) * (p[0]-o1[0]) + Math.cos(rad) * (p[1]-o1[1])) * scale + o2[1] + margin
	];
}

function cornerNode(x,y,i){
	return {
		color: "rgba(0,0,0,0)",
		size: 2,
		x: x,
		y: y,
		id: i
	};
}

module.exports = {
	clusterPacking: clusterPacking
};
