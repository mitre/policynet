'use strict';

var path 			= require('path'),
	gulp 			= require('gulp'),
	url 			= require('url'),
	proxy 			= require('proxy-middleware'),
	conf 			= require('./conf'),
	forever 		= require('forever-monitor'),
	browserSync 	= require('browser-sync'),
	browserSyncSpa 	= require('browser-sync-spa'),
	util 			= require('util'),
	proxyMiddleware = require('http-proxy-middleware'),
	$ 				= require('gulp-load-plugins')(),
	chalk			= require('chalk');

var glsObj;
var port = process.env.PORT || 5000; // set our port
function browserSyncInit() {
	var proxyOptions = url.parse('http://localhost:' + port + '/api');
		proxyOptions.route = '/api';
	browserSync.instance = browserSync.init({
		proxy: {target: "http://localhost:" + port,
				middleware: [proxy(proxyOptions)]},
	});
}

gulp.task('nodemon', ['server'], function () {
	var called = false;

	gulp.watch(path.join(conf.paths.src, '/server/js/*.js'), function(){
		setTimeout(function () {
			gulp.start('server:js');
		}, 300);
	})
	gulp.watch(path.join(conf.paths.src, '/server/java/**/*.java'), function(){
		setTimeout(function (){
			gulp.start('server:java');
		}, 300);
	})
	$.nodemon({script: '.tmp/server/js/server.js', watch: ['.tmp/server/js/server.js']});
});

browserSync.use(browserSyncSpa({
	selector: '[ng-app]'// Only needed for angular apps
}));


gulp.task('serve', ['watch', "nodemon", "server"], function () {
	browserSyncInit();
});

gulp.task('serve:dist', ['build', "server:dist"], function () {
	var child = new (forever.Monitor)('dist/server/js/server.js');
	child.on('exit', function () {
		console.log(chalk.red('PolicyNet has exited after 10 restarts.'));
	});
	child.start();
});

gulp.task('build:dist', ['build', "server:dist"]);

gulp.task('build-test', ['build','server:dist','server']);

gulp.task('serve:e2e', ['inject'], function () {
	browserSyncInit(); //[conf.paths.tmp + '/serve', conf.paths.src], []
});

gulp.task('serve:e2e-dist', ['build'], function () {
	browserSyncInit(); //conf.paths.dist, []
});
