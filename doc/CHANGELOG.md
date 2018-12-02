# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1a1] - 2018-12-02
### Added
- More detail about `config.ini` to README.md, explains what the options actually are for

### Changed
- separate `main.py` into `main` function and `make` function, to separate concerns; 
the `main` function deals with command-line parsing and `config.ini` file loading, whereas 
the `make` function just accepts the already-loaded config. That way you can call the 
`make` function with a `ConfigParser` instance regardless of its origins (e.g. if you need 
to write tests for `make` )

## [0.1] - 2018-10-24
### Added
- Original version