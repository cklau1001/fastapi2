# Introduction
This is the package to hold all database related modules. Entry point is DBEngine of database.py that get
the db_driver from a factory. It then encapsulates the implementation details of different database drivers, e.g.
postgres (sync / async) or sqlite.

All database settings are stored in .env through python dotenv module, so that the configuration is separated from
the underlying logic, and facilitate easy driver switching.

Singleton by importing target instance is used to ensure that only a single copy of database engine is used by the application.

```shell

+ db
    + adapter/
        + postgres_async.py   # to implement the dbengine and session of Postgres Async driver
    + database.py  # main entry point
    + db_driver.py  # define the interface of each database driver using abstract class
    + dbdriver_factory.py # the factory to return target db_driver.
    + models.py  # define all tables needed by this application
    
```