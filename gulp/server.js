'use strict';

var path = require('path');
var gulp = require('gulp');
var conf = require('./conf');

var $ = require('gulp-load-plugins')();

var wiredep = require('wiredep').stream;
var _ = require('lodash');

gulp.task('server', ['server:js', 'server:other', 'server:java']); // development server

gulp.task('server:dist', ['server:dist:js', 'server:dist:other', 'server:dist:java']) //

gulp.task('server:js', ['server:other'], function(){
	return gulp.src(path.join(conf.paths.src, '/server/js/server.template.js'))
    .pipe($.replace("/* express static path 1 */","\n\
app.use(express.static('" + path.resolve(conf.paths.tmp + '/client/serve/') + "'));\n\
app.use(express.static('" + path.resolve(conf.paths.src) + "'));\n\
app.use('/bower_components', express.static('" + path.resolve('bower_components') + "'));"))
    .pipe($.replace("/* main index file */",path.resolve(conf.paths.tmp + '/client/serve/index.html')))
    .pipe($.rename("server.js"))
    .pipe(gulp.dest(conf.paths.tmp + "/server/js"));
})

gulp.task('server:dist:js', function(){
	return gulp.src(path.join(conf.paths.src, '/server/js/server.template.js'))
    .pipe($.replace("/* express static path 1 */","app.use(express.static('" + path.resolve(conf.paths.dist + "/client") + "'));"))
    .pipe($.replace("/* main index file */",path.resolve(conf.paths.dist + "/client/index.html")))
    .pipe($.rename("server.js"))
    .pipe(gulp.dest(conf.paths.dist + "/server/js"));
})


gulp.task('server:other', function(){
	return server_other(conf.paths.tmp);
})

gulp.task('server:dist:other', function(){
	return server_other(conf.paths.dist);
})

gulp.task('server:java', ["build:java"], function(){
	return server_java(conf.paths.tmp);
})

gulp.task('server:dist:java', ["build:java"], function(){
	return server_java(conf.paths.dist);
})

gulp.task('build:java', function(){
	return gulp.src(path.join(conf.paths.src, 'server/java/build.sh'))
		.pipe($.shell(['sh <%= file.path %>']));
})


var server_other = function(dest_path){
	return gulp.src([path.join(conf.paths.src, '/server/js/*.js'),
					 path.join('!' + conf.paths.src, '/server/js/server.template.js')])
		.pipe(gulp.dest(dest_path + "/server/js"));
}

var server_java = function(dest_path){
	return gulp.src(path.join(conf.paths.src, 'server/java/policynet-layout/target/*with-dependencies.jar'))
		.pipe($.rename("policynet-layout.jar"))
		.pipe(gulp.dest(dest_path + "/server/java"));
}
