# netrunner

Python library and scripts for interacting with various Netrunner services.

## Library

The library has a few components:

* `netrunner.alwaysberunning`: Wrapper for [AlwaysBeRunning.net](https://alwaysberunning.net/) for getting tournaments and results
* `netrunner.netrunnerdb`: Wrapper for [NetrunnerDB](https://netrunnerdb.com/) for getting card and decklist data

## Scripts

* `scripts/cluster.py`: k-means clustering for completed tournament decklists.