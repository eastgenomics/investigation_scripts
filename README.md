# investigation_scripts

Collection of scripts and notebooks used in investigations

## Warning

**Please don't commit plots or datasets**

This is a repository for the following:
- analysis scripts (e.g. `.py`, `.sh`, `.R`, etc.)
- notebooks with rendered content removed (e.g. `.ipynb`, `.Rmd` etc.)
- _records_ of dependencies
  - e.g. `requirements.txt` (from `pip freeze`), `.Rproj`, Dockerfiles etc., _not_ the dependencies themselves

Please do not commit any of the following:
- non-plaintext files (e.g. `.png`, `.pdf`, `.tar.gz`, etc.).
- datasets in any format (including `.csv` or `.tsv`)

A good rule-of-thumb to use is as follows - if you can't read a file with a plain text editor, then you can't see how it changed. This means `git` can't either, rendering it ineffective with respect to its change-tracking abilities. If this is the case, then don't commit that file.

# Guidelines

The following guidelines suggest some approaches to ensuring your scripts and notebooks are documented alongside the dependencies required to run them.

## Python

You should always start by setting up a `venv` (or `conda` environment, docker image etc.):

```
cd my_investigation
python3 -m venv venv
source venv/bin/activate
```

Install of the requirements for your script to run using (e.g.) `pip`. When you've finished your investigation, and you're satisfied that you have all of the required dependencies, use `pip freeze > requirements.txt` to record them:

```
pip freeze > requirements.txt
```

Then commit `requirements.txt` to the repo. Future investigators will be able to use `pip install -r requirements` to replicate your python environment.

For Jupyter notebooks: strip the output before committing (**TODO: add easy method for doing this**)

## R

The following assumes you are working in RStudio on a notebook.

If so, the workflow should look a bit like this:

- Open RStudio
- Select _New Project_, and tick "_Use renv with this project_"
- Whenever you install a new package, run `renv::snapshot()`
  - This updates `renv.lock`
  - It's the `renv` equivalent of Python's `pip freeze > requirements.txt`
- When your analysis is complete, commit the following files:
  - `<your notebook>.Rmd`
  - `<your project>.Rproj`
  - `renv.lock`
  - `.Rprofile` 
  - `renv/settings.json` 
  - `renv/activate.R`

See the following links for details:

https://docs.posit.co/ide/user/ide/guide/environments/r/renv.html
https://rstudio.github.io/renv/articles/renv.html

## bash

**TODO: add some details on dependency management. For example - what happens when a specific version of jq is needed?**
