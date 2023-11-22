# CPSC 449 - Project 3

## Setting Up

### If Nix is installed...

```bash
nix-shell
```

Continue at [this step](#other-dependencies).

### Otherwise, if Nix is not installed...

Install Krakend and LiteFS:

```bash
./install_deps.sh
```

This will install Krakend and LiteFS into the `run/bin` directory, which is
specifically an ephemeral directory for this project.

You will also need:
- `ruby-foreman`
- Python 3 with virtualenv

### Other dependencies

Install required Python packages into a virtual environment from `pip`:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

DynamoDB Local:
1. Download "DynamoDB local v2.x" from
[here](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.DownloadingAndRunning.html)
2. Extract the .jar in the archive to the project's `./run/`

Other packages:
- `redis` - make sure the server is running
- `openjdk-19-jre-headless`

## Initialization

After installing necessary components, initialize the JWT keys...

```bash
./init_jwt_keys.sh
```

Start all the services...

```bash
foreman start
```

Then, initialize the databases...

```bash
./init_dbs.sh
```

The server has now been initialized and is running.

## Running

If the server isn't running, assuming the above steps have been taken, the
server can be started by running:

```bash
foreman start
```