# envdiff

Compare environment variable configurations across multiple deployment targets and highlight discrepancies.

## Installation

```bash
pip install envdiff
```

## Usage

Point `envdiff` at two or more environment files or live deployment targets to see what differs between them.

```bash
# Compare two .env files
envdiff compare .env.staging .env.production

# Compare multiple targets
envdiff compare .env.dev .env.staging .env.production

# Output differences as JSON
envdiff compare .env.staging .env.production --format json
```

Example output:

```
KEY                  dev          staging      production
─────────────────────────────────────────────────────────
DATABASE_URL         ✔ set        ✔ set        ✘ missing
LOG_LEVEL            debug        info         info
CACHE_TTL            300          300          ✘ missing
NEW_RELIC_KEY        ✘ missing    ✔ set        ✔ set
```

Variables are flagged as:
- **Missing** – present in some targets but absent in others
- **Mismatched** – set in all targets but with differing values
- **Consistent** – identical across all targets (hidden by default, use `--show-all`)

```bash
# Show all variables including consistent ones
envdiff compare .env.staging .env.production --show-all
```

## Configuration

Optionally create an `envdiff.toml` in your project root to define named target groups and ignore patterns:

```toml
[targets]
staging = ".env.staging"
production = ".env.production"

[ignore]
keys = ["CI_BUILD_ID", "DEPLOY_TIMESTAMP"]
```

Then simply run:

```bash
envdiff compare staging production
```

## License

MIT