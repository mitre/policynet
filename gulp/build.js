'use strict';

var path = require('path');
var gulp = require('gulp');
var conf = require('./conf');

var $ = require('gulp-load-plugins')({
	pattern: ['gulp-*', 'main-bower-files', 'uglify-save-license', 'del']
});

gulp.task('partials', function () {
	return gulp.src([
		path.join(conf.paths.src, '/app/**/*.html'),
		path.join(conf.paths.tmp, '/client/serve/app/**/*.html')
	])
		.pipe($.minifyHtml({
			empty: true,
			spare: true,
			quotes: true
		}))
		.pipe($.angularTemplatecache('templateCacheHtml.js', {
			module: 'policynet',
			root: 'app'
		}))
		.pipe(gulp.dest(conf.paths.tmp + '/client/partials/'));
});

gulp.task('html', ['inject', 'partials'], function () {
	var partialsInjectFile = gulp.src(path.join(conf.paths.tmp, '/client/partials/templateCacheHtml.js'), { read: false });
	var partialsInjectOptions = {
		starttag: '<!-- inject:partials -->',
		ignorePath: path.join(conf.paths.tmp, '/client/partials'),
		addRootSlash: false
	};

	var htmlFilter = $.filter('*.html');
	var jsFilter = $.filter('**/*.js');
	var cssFilter = $.filter('**/*.css');
	var assets;

	return gulp.src(path.join(conf.paths.tmp, '/client/serve/*.html'))
		.pipe($.inject(partialsInjectFile, partialsInjectOptions))
		.pipe(assets = $.useref.assets())
		.pipe($.rev())
		.pipe(jsFilter)
		.pipe($.ngAnnotate())
		.pipe($.uglify({ preserveComments: $.uglifySaveLicense })).on('error', conf.errorHandler('Uglify'))
		.pipe(jsFilter.restore())
		.pipe(cssFilter)
		.pipe($.csso())
		.pipe(cssFilter.restore())
		.pipe(assets.restore())
		.pipe($.useref())
		.pipe($.revReplace())
		.pipe(htmlFilter)
		.pipe($.minifyHtml({
			empty: true,
			spare: true,
			quotes: true,
			conditionals: true
		}))
		.pipe(htmlFilter.restore())
		.pipe(gulp.dest(path.join(conf.paths.dist, '/client/')));
		// .pipe($.size({ title: path.join(conf.paths.dist, '/'), showFiles: true }));
});

// Only applies for fonts from bower dependencies
// Custom fonts are handled by the "other" task
gulp.task('fonts', function () {
	return gulp.src($.mainBowerFiles())
		.pipe($.filter('**/*.{eot,svg,ttf,woff,woff2}'))
		.pipe($.flatten())
		.pipe(gulp.dest(path.join(conf.paths.dist, '/client/fonts/')));
});

gulp.task('other', function () {
	var fileFilter = $.filter(function (file) {
		return file.stat.isFile();
	});

	return gulp.src([
		path.join(conf.paths.src, '/**/*'),
		path.join('!' + conf.paths.src, '/**/*.{html,css,js,scss}'),
		path.join('!' + conf.paths.src, '{/server,/server/**}')
	])
		.pipe(fileFilter)
		.pipe(gulp.dest(path.join(conf.paths.dist, '/client/')));
});

gulp.task('clean', function (done) {
	$.del([path.join(conf.paths.dist, '/'), path.join(conf.paths.tmp, '/'), path.join(conf.paths.server, '/')], done);
});

gulp.task('build', ['html', 'fonts', 'other']);
