# Cluster

Clustering of tournament-winning decklists within a time range using the [DBSCAN](https://en.wikipedia.org/wiki/DBSCAN) algorithm.

## Usage

See the [beginner's guide](https://github.com/kirbyUK/netrunner/blob/master/BEGINNERS-GUIDE.md) for help setting up how to run this script.

The script is run with:

```sh
python -m netrunner.cluster --output "my-output-filename.md" --start-date 2024-05-31
```

## Arguments

The script has the following arguments:

* `--output` - The output markdown filename. If this is not given, it will output a file named `rwr_<end-date>.md` in the same folder the script was run from.
* `--start-date` - The start date to begin getting tournament results from (inclusive). Defaults to 2024-03-18, the release of Rebellion Without Rehersal.
* `--end-date` - The last date to get tournament results from. Defaults to the current day.
* `--format` - The format to get decklists for - standard or startup. Defaults to standard.
* `--percentage` - The top percentage of tournament swiss results to get decklists from. Defaults to 30%.
* `--eps` - The epsilon ([eps](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.DBSCAN.html)) parameter to give to DBSCAN. This defaults to 7.5, but needs careful consideration.
* `--min-samples` - The minimum number of decks to form a cluster. See the above link for further details. Defaults to 3.

## Output

The script outputs a [Markdown](https://en.wikipedia.org/wiki/Markdown) file with the determined clusters, and the top 10 cards of each cluster.

Markdown is a common format and can be read with just a text editor like Notepad, or if you want formatting you could copy-and-paste the output to [StackEdit](https://stackedit.io), or anything else that can render Markdown.

## The eps and min-samples parameters

The `--eps` parameter is key to how the clusters are decided. The larger the number, the greater the distance allowed between two points to be considered in the same cluster. The default value of 7.5 was useful for the RWR meta from release to just before the banlist. When there's less data, e.g. just after a banlist comes out, you might need to increase it to get decks to stick together. If you have the value too high, you might have decks that seem unrelated start to group together. For example, Precision Design and Sportsmetal decks can start to be in the same cluster if the value is big enough. Whether this is correct or not is really up to you. The best thing to do is experiment with the parameter.

The `--min-samples` parameter determines the minimum number of decks that need to form a cluster. If you set it to 1, every deck will have a cluster, meaning you might end up with many random off-meta decks that have not seen repeated success. Again, experiment and use a value that generates what you'd like.

## Notes

This script is a very close analouge to what's presented in Luciano Strika's [K-Means Clustering for Magic: the Gathering Decks](https://strikingloo.github.io/k-means-clustering-magic-the-gathering). That blog mostly looks to determine if a card would be good in a given deck, whereas the purpose of this script as I see it is as a crude "what's the meta" button - something to be run that determines the common winning decks and what they're running.

My main change from that article is switching from k-means clustering to DBSCAN, because I wanted something that could determine the number of clusters itself, be deterministic on multiple runs, and the noise elimination to filter out outliers.

An annotated example of the output between `2024-03-18` and `2024-05-12` can be seen [here](https://wiki.3t.network/books/netrunner/page/standard-metagame-2024-05-12). The script does not name the clusters, that has to be done manually.

It should be said I'm not a data scientist! I just twiddled the values until I got output that seemed correct to me. Any and all contributions welcome!

Examples of things I'd like in the future:

* Visualisations of the clusters
* Tieing the data to winrates, etc.
* Further statistics