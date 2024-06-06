# Beginner's Guide

If you've never run any Python program before but would like to run the code here, please follow this guide.

## 1. Install Python

Download and install Python 3 from [here](https://www.python.org/downloads/).

**For Windows users**: During the install, be sure to click "Add python.exe to PATH" at the bottom of the first installer page.

## 2. Download this repository

If you're familiar with git, you can `git clone` this repository like normal.

If not, you can download the repository as a ZIP file with [this](https://github.com/kirbyUK/netrunner/archive/refs/heads/master.zip) link. Extract the ZIP to wherever you like.

## 3. Install the Netrunner package

From here on out, we will need the commandline. We ideally need to be in the folder containing the code you downloaded in step 2.

**Windows users** there is a convenient shortcut, if you hold Shift and Right-Click in the folder, you can click "Open in Terminal" or "Open Powershell window here" to get a terminal where you need it.

If that doesn't work, or you're on Linux or Mac, you can instead use the `cd` command to change to the right folder. For example, if I extract the code to `C:\Users\alex\Documents\netrunner`, I would use:

```
cd C:\Users\alex\Documents\netrunner
```

As you're typing commands, you can press the Tab button to auto-complete sections.

Once your terminal is in the right place, run this command to install the code:

```
python -m pip install .
```

If this completes successfully, you're ready to start running the code.

## 4. Run the script

For this we'll be using the [netrunner.cluster](https://github.com/kirbyUK/netrunner/tree/master/netrunner/cluster) script as our example.

To run the script, use the name of the script like so:

```
python -m netrunner.cluster
```

This will run the script with default settings. If you'd like to change the settings, put the options you'd like to change in any order after the command, with a space separating the option name and the new value. For example, to run the cluster script with a new start date and a higher eps value, you'd do:

```
python -m netrunner.cluster --start-date 2024-05-31 --eps 9.5
```

See the individual script's documentation for more information on allowed options, or run the script with the `--help` flag.

If the script writes a file, by default it will be in the same folder you ran the script from. You can change this with the `--output` option.