var express 		= require("express"),
	socket			= require("socket.io"),
	http			= require("http")
	bodyParser 		= require("body-parser"),
	path			= require("path"),
	events			= require("events"),
	helmet			= require("helmet"),
	app 			= express(),
	server			= http.createServer(app),
	io				= socket(server),
	config			= require('./config.js'),
	utils			= require('./utils.js'),
	logic			= require('./query.logic.js'),
	dashboard		= require('./dashboard.js');

global.emitter		= new events.EventEmitter().setMaxListeners(50);

var port = process.env.PORT || 5000; // set our port

app.use(bodyParser.json()); // parse application/json
app.use(bodyParser.json({ type: 'application/vnd.api+json' })); // parse application/vnd.api+json as json
app.use(bodyParser.urlencoded({ extended: true })); // parse application/x-www-form-urlencoded
app.use(helmet());
//----- Socket Processor ------------------------------------------------------
// io.on('connection', function(client){
// 	emitter.on('message', function(message){
// 		client.emit('message',message);
// 	})
// 	console.log("client at %s connected",client.handshake.address);
// })
//----- end Socket Processor --------------------------------------------------


//----- API Router ------------------------------------------------------------
var api = express.Router();

//----- ### API Configuration -------------------------------------------------
api.use(function(req, res, next) {
	// res.setHeader('Access-Control-Allow-Origin', '*');
	// res.setHeader('Access-Control-Allow-Headers', '*');
	next();
});

api.get('/', function(req, res) {
	res.json({ message: 'hooray! welcome to our api!' });
});
api.get('/sections', logic.request("sections"));
api.get('/neighborhood', logic.request("network_neighborhood"));
api.get('/network', logic.request("network_es"));
api.get('/network_neo4j', logic.request("network_neo4j"));
api.get('/node', logic.request("node"));
api.get('/suggest', logic.request("suggest"));
api.get('/parseQuery', logic.request("parseQueryWrapper"));
api.get('/visit', logic.request('visit'));
api.get('/table_stats', logic.request("table_stats"));
// api.get('/download', logic.download);

api.get('/bill_search', logic.request("bill_search"));
api.get('/bill_get', logic.request("bill_get"));
api.get('/get_text', logic.request("get_text"));
app.use('/api', api);

//----- end API Router --------------------------------------------------------
//----- ### Error handler -----------------------------------------------------
app.use(function(err, req, res, next){
	utils.error(err.message);
	utils.error(err.stack);
	res.status(500).send("Internal Server Error.");
})
//----- end Error handler -----------------------------------------------------

//----- load static pages -----------------------------------------------------
//----- ### static paths: Do not delete the following line --------------------
/* express static path 1 */
//----- ### end static paths---------------------------------------------------

//----- ### default page ------------------------------------------------------
app.get('*', function (req, res) {
	res.sendFile('/* main index file */');
});
//------ end static------------------------------------------------------------

server.listen(port);
utils.success("Server started on port "+port+"!");
