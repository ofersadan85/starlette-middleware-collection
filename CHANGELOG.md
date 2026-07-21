# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
<!-- markdownlint-disable MD024 -->

## [Unreleased](https://github.com/ofersadan85/starlette-middleware-collection/tree/main)

### Added

- Per-middleware documentation pages on the docs site, generated from module doc strings.

### Changed

### Removed

## [v0.2.0](https://github.com/ofersadan85/starlette-middleware-collection/tree/v0.2.0) - 2026-07-21

### Added

- `ResponseUUID`: Middleware that generates a UUID for each outgoing response and attaches it to the response headers. Propagates the request UUID if `RequestUUID` middleware is also used, ensuring consistent tracking of requests and responses.
- `ResponseTime`: Middleware that measures the time taken to process each request and adds this information to the response headers.
- `RequestLogging`: Middleware that logs incoming requests and outgoing responses, including details such as method, URL, status code, and processing time. Allows for configurable log formats and backends, enabling integration with various logging systems.

## [v0.1.2](https://github.com/ofersadan85/starlette-middleware-collection/tree/v0.1.2) - 2026-07-08

### Added

- First release of the package, including the following middleware components:
  - `RequestUUID`: Middleware that generates a UUID for each incoming request and attaches it to the request state.
  - `SizeLimit`: Middleware that limits the size of incoming requests to prevent abuse and ensure efficient resource usage.
