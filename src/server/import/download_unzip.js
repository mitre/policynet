var unzip 		= require('unzip2'),
	promise 	= require('bluebird'),
	rp 			= require('request-promise'),
	cheerio		= require('cheerio'),
	// wget		= require('wget'),
	// wget		= require('node-wget'),
	// wget		= require('wget-improved'),
	fs			= require('fs'),
	http 		= require('http'),
	request 	= require('request'),
	_ 			= require('lodash'),
	rimraf		= require('rimraf'),
	config 		= require('../js/config.js');

function download_unzip(){
	return new promise(function(resolve, reject){
		var promises = [];
		var zip_path_prefix = "/tmp/";
		promises.push(new promise(function(resolve, reject){
			return rp(_.extend({
				uri: "http://uscode.house.gov/download/download.shtml",
				method: 'get'
			}, config.http_options)).then(function(usc_html){
				var $ = cheerio.load(usc_html);
				var usc_link = "http://uscode.house.gov/download/" + $("[title='All USC Titles in XML']").attr("href");
				var zip_path = zip_path_prefix + "usc.zip";
				download(usc_link, zip_path).then(function(){
					fs
					.createReadStream(zip_path)
					.pipe(unzip.Extract({path: zip_path + "_unzipped"}))
					.once("error", function(){
						console.error("unable to uncompress .zip file", zip_path)
					})
					.on("close", function(){
						delete_file(zip_path);
						resolve();
					})
				});

			})
			.catch(function(err){
				console.error(err);
				delete_file(zip_path);
				reject(err);
			});
		}));

		promises.push(new promise(function(resolve, reject){
			return rp(_.extend({
				uri: "https://www.gpo.gov/fdsys/bulkdata/CFR",
				method: 'get'
			}, config.http_options)).then(function(cfr_html){
				var $ = cheerio.load(cfr_html);
				var cfr_year = $("#bulkdata > table > tr:nth-child(4) a").text().trim()
				var cfr_link = "https://www.gpo.gov/fdsys/bulkdata/CFR/" + cfr_year + "/CFR-" + cfr_year + ".zip";
				var zip_path = zip_path_prefix + "cfr.zip";
				download(cfr_link, zip_path).then(function(){
					fs
					.createReadStream(zip_path)
					.pipe(unzip.Extract({path: zip_path + "_unzipped"}))
					.once("error", function(){
						console.error("unable to uncompress .zip file", zip_path)
					})
					.on("close", function(){
						delete_file(zip_path);
						resolve();
					})
				});

			})
			.catch(function(err){
				console.error(err);
				delete_file(zip_path);
				reject(err);
			});
		}));

		promise.all(promises).then(function(){
			console.log("USC/CFR downloaded and unpacked")
			resolve();
		});
	});
}
var delete_file = function(path){
	rimraf(path, function(err){
		err && error(err.message);
		console.log("deleted " + path);
	});
}
function download(uri, output){
	return new promise(function(resolve, reject){
		var file = fs.createWriteStream(output);
		console.log("start to download", uri, "to", output);
		request(_.extend({
			url: uri,
		}, config.http_options)).pipe(file);
		file.on('finish', function(){
			file.close(function(){
				resolve();
			});
		});
		file.on('error', function(err){
			console.error(err);
			reject(err);
		});
	});
}

module.exports = {
	download_unzip: download_unzip,
	delete_file: delete_file
};
