mongo_engine_lite
=================
MongoEngine Lite helps create a lite version of a Mongo database, similar to SQLite to SQL databases. MongoEngine Lite is a wrapper over MongoEngine ORM and persists the information to a JSON file in the project's root.

To connect to the database, use

    from mongoenginelite import connect

    connect('dbname')

Documents and EmbeddedDocuments can be used in the same way that MongoEngine does. Nothing else is necessary.
