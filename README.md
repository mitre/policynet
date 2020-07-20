PolicyNet
=========

# [Demo](http://policynet.mitre.org/intro).

## Requirements

* JDK 1.8 (`java-1.8.0-openjdk` & `java-1.8.0-openjdk-devel`) + maven
* node.js + npm
* Python2.7 + pip + virtualenv
* Neo4J
* Elastic
* PostgreSQL

## Install

```bash
$ npm install
```
### Copy the sample configuration file and make appropriate changes
```bash
$ cp src/server/js/config.example.js src/server/js/config.js
```
### Ingest data
#### Make sure Neo4J, Elastic, and PostgreSQL are up and running. A PostgreSQL user and an empty PostgreSQL database (that the user has access to) is required.
```bash
$ node src/server/import/import.js pg_user pg_pass pg_database
```
An alternative import mechanism (for PostgreSQL -> Neo4J stage) is provided, which our tests have shown to be more performant on OS X (but less performant on CentOS).
```bash
$ node src/server/import/import.js pg_user pg_pass pg_database alt
```

## Usage

```bash
$ export PORT=8080 # (optional) set port. Needs privilaged user to bind to port < 1024
$ npm run serve # production
$ npm start # development
$ npm restart # restart development if server did not recover from fault
```

### Known Issues

* none
