var _ 				= require('lodash'),
	moment			= require('moment'),
	utils			= require('./utils.js'),
	query_utils		= require('./query.utils.js');

var all = function(req, res){
	query_utils.mongoose_find('log',{
		select: {
			'_id': 0,
			req_time: 1,
			parameters: 1,
			api: 1,
			URL: 1,
			IP: 1,
			sessionID: 1,
			timestamp: 1
		},
		sort: {
			timestamp: 1
		}
	}).then(function(results){
		try {
			res.json({
				start_time: results[0].timestamp,
				end_time: results[results.length - 1].timestamp,
				words: get_words(results),
				action_freq: get_action_freq(results),
				visitors_time: get_visitors_time(results),
				visit_freq: get_visit_freq(results),
				visitors_day: get_visitors_day(results)
			})
		} catch (err){
			utils.error(err.message);
			utils.error(err.stack);
		}
	}, function(err){
		res.status(500).json(err);
	})
}

var date_range = function(req, res){
	var start_date = req.query.start_date,
		end_date = req.query.end_date;

	query_utils.mongoose_find('log',{
		query: {
			timestamp: {$gte: start_date, $lte: end_date}
		},
		select: {
			'_id': 0,
			req_time: 1,
			parameters: 1,
			api: 1,
			URL: 1,
			IP: 1,
			sessionID: 1,
			timestamp: 1
		},
		sort: {
			timestamp: 1
		}
	}).then(function(results){
		res.json({
			start_time: results[0].timestamp,
			end_time: results[results.length - 1].timestamp,
			words: get_words(results),
			action_freq: get_action_freq(results),
			visitors_time: get_visitors_time(results),
			visit_freq: get_visit_freq(results),
			visitors_day: get_visitors_day(results)
		})
	}, function(err){
		res.status(500).json(err);
	})
}

var get_words = function(results){
	var words = {};
	results.forEach(function(result){
		if (result.parameters && result.parameters.query){
			_.words(result.parameters.query).forEach(function(word){
				if (words[word]){
					words[word] ++;
				} else {
					words[word] = 1;
				}
			});
		}
	});

	return _.transform(words, function(result, size, text){
		result.push([text, size]);
	}, []);
}
var get_action_freq = function(results){
	var out = {categories: [], data: []};
	results.forEach(function(result){
		var ind = _.indexOf(out.categories, result.api);
		if (ind >= 0){
			out.data[ind] ++;
		} else {
			out.categories.push(result.api);
			out.data.push(1);
		}
	});
	return out;
}
var get_visitors_time = function(results){
	var count = 0,
		visitors = [],
		out = [];
	results.forEach(function(result){
		if (!_.includes(visitors, result.sessionID)){
			visitors.push(result.sessionID);
			count ++;
			out.push([result.timestamp, count]);
		}
	});
	return out;
}

var get_visitors_day = function(results){
	var last_time,
		count = 0,
		visitors = [],
		out = [];

	results.forEach(function(result){
		last_time = last_time || moment(result.timestamp);
		if (!moment(result.timestamp).isSame(last_time, 'day')){
			out.push([last_time.startOf('day').valueOf(), count]);
			count = 0;
			visitors = [];
			last_time = moment(result.timestamp);
		}
		if (!_.includes(visitors, result.sessionID)){
			visitors.push(result.sessionID);
			count ++;
		}
	});
	out.push([last_time.startOf('day').valueOf(), count]);
	return out;

}

var get_visit_freq = function(results){
	var out = {categories: [], data: []};
	results.forEach(function(result){
		if (result.api === "visit"){
			var ind = _.indexOf(out.categories, result.parameters.page);
			if (ind >= 0){
				out.data[ind] ++;
			} else {
				out.categories.push(result.parameters.page);
				out.data.push(1);
			}
		}
	});
	return out;
}
module.exports = {
	all: all,
	date_range: date_range
}
