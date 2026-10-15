# tap-acumatica

A [Singer](https://www.singer.io/) tap that extracts data from **Acumatica**. It is built with [hotglue-singer-sdk](https://github.com/hotgluexyz/HotglueSingerSDK) and speaks the standard Singer message protocol on stdout, so you can pair it with any compatible target.

## Features

- **REST**-style HTTP streams (see `client.py` / `streams.py`).
- **OAuth2** with access token support via Hotglue (`access_token_support` on the tap).

- Required **`api_url`** and optional **`start_date`** (see [Configuration](#configuration)).
- Account and vendor syncs use the entity GUID **`id`** as the primary key and **`LastModifiedDateTime`** as the replication key.

### Streams

| Stream | Endpoint / notes | Primary key | Replication key |
| ------ | ---------------- | ----------- | ----------------- |
| `accounts` | `GET` `{api_url}/entity/Default/{version}/Account` | `id` | `LastModifiedDateTime` |
| `companies` | `PUT` `{api_url}/entity/Default/{version}/CompaniesStructure` | `id` | — |
| `vendors` | `GET` `{api_url}/entity/Default/{version}/Vendor` | `id` | `LastModifiedDateTime` |

Account and vendor records are paged with `$top` and `$skip` (100 per page). Incremental syncs send `$filter=LastModifiedDateTime ge {bookmark}`. Field values are unwrapped from Acumatica's `{"value": ...}` objects before they are emitted. Vendor requests expand attributes, contacts and their addresses, the main, primary, remittance, and shipping contacts and their addresses, and payment instructions. Account has no linked records to expand. Companies come from the Company Branch inquiry: one `PUT` with `Results` expanded returns every branch, and the stream keeps one record per company `id` with the company fields only. That screen has no replication field.

## Requirements

- Python **3.10+** (see `requires-python` in `pyproject.toml`).

## Installation

1. **Clone** this repository and `cd` into the project directory.
2. **Create `config.json`** in the project root with your credentials and settings (see [Configuration](#configuration) for the fields and an example).
3. **Create a virtual environment** and activate it:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows, use `.venv\Scripts\activate` instead of `source .venv/bin/activate`.

4. **Install the package** in editable mode:

```bash
pip install -e .
```

5. **Run the tap** (with the venv still activated):

```bash
tap-acumatica --help
```

## Configuration

| Setting | Type | Required | Default | Description |
| ------- | ---- | -------- | ------- | ----------- |
| `start_date` | string (datetime) | no | `2000-01-01T00:00:00Z` | Earliest record date to sync. |
| `api_url` | string | yes | — | Acumatica site URL. A trailing slash is ignored. |
| `client_id` | string | yes | — | OAuth client ID. |
| `client_secret` | string | yes | — | OAuth client secret. |
| `refresh_token` | string | no | — | OAuth refresh token (if applicable). |

Run `tap-acumatica --about` (or `tap-acumatica --about --format=markdown`) for the authoritative schema for your installed version.

### Example `config.json`

```json
{
  "start_date": "2000-01-01T00:00:00Z",
  "api_url": "http://host/AcumaticaSandbox",
  "client_id": "YOUR_CLIENT_ID",
  "client_secret": "YOUR_CLIENT_SECRET",
  "refresh_token": ""
}
```

Do not commit real credentials. Prefer environment variables or a secrets manager in production.

### Environment-based config

You can load settings from the process environment using `--config=ENV` (the SDK merges env into config). Env names follow the tap’s setting keys (see `tap-acumatica --about`).

## Usage

With your virtual environment **activated** and `config.json` in place:

Discover stream catalog:

```bash
tap-acumatica --config config.json --discover > catalog.json
```

Run a sync (with optional state):

```bash
tap-acumatica --config config.json --catalog catalog.json --state state.json
```

Pipe to any Singer target:

```bash
tap-acumatica --config config.json --catalog catalog.json | target-jsonl
```

Inspect built-in settings and stream metadata:

```bash
tap-acumatica --about
```

## API / documentation

`api_url` is the required Acumatica site root. The tap reads `{api_url}/entity` once and calls the latest `Default` contract version. The OAuth token endpoint is `{api_url}/identity/connect/token`.


## License
Apache 2.0 — see `LICENSE` and `pyproject.toml`.
