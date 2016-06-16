module.exports = {
	java_home	: process.env.JAVA_HOME || "/usr/lib/jvm/java-1.8.0-openjdk.x86_64/",
	neo4j_url	: 'http://localhost:7474',
	elastic_host: 'localhost:9200',
	sunlightapi	: {
		api_key: "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
		url: "http://congress.api.sunlightfoundation.com",
		bill_search: "/bills/search",
		bill_get: "/bills"
	},
	http_options: {
	},
	commit: "production" // or specific commit
};
