# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0a1] 2019-02-04
### Added
- More detail about `config.ini` to README.md, explains what the options actually are for
- `.json` file saved by searchstims has more info about stimuli, such as location
  of targets and distractors (in case this is needed for analysis)
- unit tests

### Changed
- separate `main.py` into functions, to separate concerns; 
  * the `main` function deals with command-line args
  * `parse_config` loads and parses `config.ini` files 
  * `make` function accepts parsed config
  * This way you can call the `make` function with a `ConfigTuple` instance
   regardless of its origins (e.g. if you need to write tests for `make` )
- command-line interface now requires name of config file as first arg, instead of 
  specifying it with optional `-c` flag (vestige of when I didn't understand how 
  `argparse` is meant to work)

### Fixed
- indent error in `main.py` that caused crash when `stimulus = rectangle`

## [0.1] - 2018-10-24
### Added
- Original version