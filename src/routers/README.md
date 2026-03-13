# Introduction
This folder holds the routes (URL) of each endpoint. A file-based routing is used so that
if v2 is needed in future, the v2 routes can then be placed into that directory with
fastapi app pointing to it. That can also simplifies rollback to previous version.
