# version-check

A simple tool to search [Salt](https://github.com/saltstack/salt) branches
and tags for pull requests.

This tool outputs the list of branches and/or tags that the provided
pull request or git commit is found in.

A git fetch is performed at the beginning of the main Python function. This
provides the most up-to-date search results for the given pull request
or commit sha.

## Installation

The following steps will walk you through building the Docker image needed
to use this tool.

These step assume Docker is already installed. If you haven't previously
installed Docker, follow these [installation instructions](https://docs.docker.com/engine/installation/).

1. First, clone this repo. Then, change directories to the new clone:
```
$ git clone https://github.com/rallytime/version-check.git
$ cd version-check/
```
1. Next, build the Docker container:
```
$ docker build -t version_check .
```

You should now be ready to use version_check to find branches and tags that
your pull request is contained in.

## Usage

The Docker build above copies `version_check.py` into the image and sets
an `entrypoint` to run the file with Python. That way, you can provide the
script arguments for the tool directly to the container:
```
$ docker run --rm -it version_check -h
```

### Options

The version_check tool allows you to provide a pull request number or a commit
hash (but not both).

PR Example:
```
$ docker run --rm -it version_check -p 42890
Branches:
  2016.11
  2016.11.8
  2017.7
  2017.7.2
  develop
Tags:
  v2016.11.8
  v2017.7.2
```

Commit Example (same PR number, but using a commit instead):
```
$ docker run --rm -it version_check -c 999388680ca67d9d2aafa6c0fbc3acc5d8389208
Branches:
  2016.11
  2016.11.8
  2017.7
  2017.7.2
  develop
Tags:
  v2016.11.8
  v2017.7.2
```

You can also narrow your search to scan specific branches or tags:
```
$ docker run --rm -it version_check -p 42890 -b 2017.7 -t v2016.11.8
Branches:
  2017.7
Tags:
  v2016.11.8
```

Multiple branches or tags can also be provided:
```
$ docker run --rm -it version_check -p 42890 -b 2017.7 -b develop
Branches:
  2017.7
  develop
```
