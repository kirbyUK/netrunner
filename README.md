# netrunner

Python library and scripts for interacting with various Netrunner services.

## Library

The library has a few components:

* `netrunner.alwaysberunning`: Wrapper for [AlwaysBeRunning.net](https://alwaysberunning.net/) for getting tournaments and results
* `netrunner.netrunnerdb`: Wrapper for [NetrunnerDB](https://netrunnerdb.com/) for getting card and decklist data

## Scripts

### Cluster

Clustering of tournament-winning decklists within a time range using the DBSCAN algorithm.

The script, `netrunner-cluster`, has the following arguments:

* `--output` - The output markdown filename
* `--start-date` - The start date to begin getting tournament results from (inclusive). Defaults to 2024-03-18, the release of Rebellion Without Rehersal.
* `--end-date` - The last date to get tournament results from. Defaults to the current day.
* `--format` - The format to get decklists for - standard or startup. Defaults to standard.
* `--percentage` - The top percentage of tournament swiss results to get decklists from. Defaults to 30%.
* `--eps` - The epsilon ([eps](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.DBSCAN.html)) parameter to give to DBSCAN. This defaults to 7.5, but needs careful consideration.
* `--min-samples` - The minimum number of decks to form a cluster. See the above link for further details. Defaults to 3.

The script outputs a markdown file with the determined clusters, and the top 10 cards of each cluster.

#### Notes

This script is a very close analouge to what's presented in Luciano Strika's [K-Means Clustering for Magic: the Gathering Decks](https://strikingloo.github.io/k-means-clustering-magic-the-gathering). That blog mostly looks to determine if a card would be good in a given deck, whereas the purpose of this script as I see it is as a crude "what's the meta" button - something to be run that determines the common winning decks and what they're running.

My main change from that article is switching from k-means clustering to DBSCAN, because I wanted something that could determine the number of clusters itself, be deterministic on multiple runs, and the noise elimination to filter out outliers.

An annotated example of the output between `2024-03-18` and `2024-05-12` can be seen [here](https://wiki.3t.network/books/netrunner/page/standard-metagame-2024-05-12). The script does not name the clusters, that has to be done manually.

It should be said I'm not a data scientist! I just twiddled the values until I got output that seemed correct to me. Any and all contributions welcome!

Examples of things I'd like in the future:

* Visualisations of the clusters
* Tieing the data to winrates, etc.
* Further statistics