# Grocery Bot (name TBD)

A simple telegram bot application for Cabin's adhoc grocery needs.

## High Level Objectives:

### Behavioral:

* Someone requests a grocery item by calling to `/order`
* Someone can pull everything currently in the queue by calling `/print`
* This command prints the list to a receipt printer and/or sends it in a DM
* Once an item is printed, it exits the queue

### Technical:

* Async read/writes from/to a local SQLite DB
* Caching in Pandas for quick read/writes
* How the fuck does a receipt printer work man