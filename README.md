git2labnotebook
===============

Forced to write a lab notebook while only doing computer work?

Parse all your commits from various projects and make them into daily summaries of your activity, ready to print into a lab notebook. Yay \o/

## Install
```sh
pip install git+git://github.com/afrendeiro/git2labnotebook.git [--user]
```

## Usage

To see all options:
```sh
git2labnotebook --help
```

Common usage: just point to the root directory containing your git repos:
```sh
git2labnotebook -d /home/afr/workspace/
```

Keep only commits by username (e.g. afrendeiro):

```sh
git2labnotebook -u afrendeiro -d /home/afr/workspace/
```

Exclude particular repositories from records:
```sh
git2labnotebook -fr afrendeiro.github.io -d /home/afr/workspace/
```

Limit commits to within particular dates (from-to, YYYYMMDD format):
```sh
git2labnotebook -f 20140915 -t 20170915 -d /home/afr/workspace/

```

## Features
If `pandoc` is installed, conversion to DOCX and PDF (through Latex) formats will be performed.
DOCX has a sensible template so it's ready to print.
A nice Latex template will follow!
