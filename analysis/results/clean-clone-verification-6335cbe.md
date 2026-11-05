# Clean-clone verification — commit `6335cbe`

Date: 2026-11-05

## Fresh clone

The private GitHub repository was cloned into a temporary scratch directory:

```text
C:\Users\rajiv\AppData\Local\hermes\cache\scratch\sugen-clean-6335cbe
```

Verified:

- cloned from `mantramehtapy/sugen-icd11-assessment`;
- HEAD: `6335cbe38c1f32caf7246ad833895369d7327a52`;
- working tree clean;
- branch `main` tracks `origin/main`.

## Docker gate

The first prerequisite command was:

```bash
docker version --format '{{.Server.Version}}'
```

Observed failure:

```text
failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine;
check if the path is correct and if the daemon is running:
open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.
```

Because the Docker daemon is not running or not reachable on this machine, these commands were **not executed** and must not be reported as passed:

```bash
docker compose config --quiet
docker compose build --no-cache coder
docker compose run coder /in/notes.jsonl /out/predictions.jsonl
```

## Status

- Fresh Git clone: **PASS**
- Docker daemon availability: **BLOCKED**
- Clean-clone Docker build/run: **OPEN**
- Supplied scorer from the clean Docker output: **OPEN**

This is a verified environment blocker, not a simulated Docker result. Start Docker Desktop and rerun the exact commands before submission.
