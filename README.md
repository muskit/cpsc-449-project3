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

```console
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

DynamoDB Local:
1. Download "DynamoDB local v2.x" from
[here](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.DownloadingAndRunning.html)
2. From the archive, extract both `DynamoDBLocal.jar` and the `DynamoDBLocal_lib`
folder into a new folder `dynamodb_local` at the project's root.

Other packages:
- `redis` - make sure the server is running
- `openjdk-19-jre-headless`

## Initialization

Make sure you're in the virtual environment.

```bash
$ which python
.../.venv/bin/python

# if output doesn't contain a string like the above...
$ source .venv/bin/activate
```

First, run `aws configure`, and setup using dummy credentials
(go [here](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-quickstart.html#getting-started-quickstart-new-command)
and look under the "Long-term credentials " tab).

Make sure the Redis service is running:
```console
# systemctl start redis
```

Run the pre-start init script...

```console
$ ./init_pre_start.sh
```

Start all the services...

```console
$ foreman start
```

Then, in another terminal, run the post-start init script:

```console
$ source .venv/bin/activate
$ ./init_post_start.sh
```

The server has now been initialized and is running.

You may optionally create test data in the Enrollments system:
```console
$ ./insert_enrollment_test_data.sh
```

## Running

If the server isn't running, assuming the application has already
been initialized and you're in the virtual environment, the
server can be started by running:

```console
$ foreman start
```

Make sure the Redis service is also running:
```console
# systemctl start redis
```