# Kafka events analyzer (KEA)

- [Kafka events analyzer (KEA)](#kafka-events-analyzer-kea)
  - [Example](#example)
  - [|*Message bus* | implements publisher-subscriber communication pattern  | kafka+zookeeper |](#message-bus--implements-publisher-subscriber-communication-pattern---kafkazookeeper-)
  - [Implementation details](#implementation-details)
    - [Dependencies](#dependencies)
  - [Configuration and running](#configuration-and-running)
    - [States definitions example (states.def)](#states-definitions-example-statesdef)
    - [Expectation example (expected.txt)](#expectation-example-expectedtxt)
    - [Kafka configuration (config.ini)](#kafka-configuration-configini)
    - [Running the analyzer](#running-the-analyzer)
      - [Local runtime environment](#local-runtime-environment)
      - [Docker container](#docker-container)
    - [VSCode debug session configuration](#vscode-debug-session-configuration)
  - [Support](#support)

A tool for monitoring and checking events in Kafka message bus. KEA works in combination with [sequence checker](https://github.com/sergey-sobolev/sequence_checker).

The main purpose of the tool is validation of system events  against pre-defined (expected) sequences.

## Example

Let's consider [secure update](https://github.com/sergey-sobolev/secure-update) implementation. It consists of the following components:

| Name | Purpose | Comment |
|----|----|----|
|*File server* | contains update files | external to the system, imitates some web server out there in Internet |
|*Application* | application to be updated | a stub, no real business logic, just something to be able to check that it works and got updated (or not) |
|*Updater* | actually applies an update | must work in the same container with the *Application*, to be able to modify its files |
|*Downloader*  | downloads update files from external network | in this example - from the *File server* |
|*Manager* | orchestrates the update process | |
|*Verifier* | verifies correctness of an update file | |
|*Storage* | stores the update file(s) internally | |
|*Security monitor* | checks every message in the message bus, authorizes further processing if no rules violated, blocks otherwise  | |
|*Message bus* | implements publisher-subscriber communication pattern  | kafka+zookeeper |
---

Normal update process will have the following sequence
![Sequence diagram](./docs/diagrams/docs/update-sd/update-sequence.png?raw=true "Sequence diagram")

In terms of events exchange in the message bus it would like this:

```
manager->downloader->manager->storage->manager->verifier->storage->verifier->manager->updater->storage->updater
```

If each update request has UUID, then the whole sequence can be traced using the UUID as a correlation ID.

Then if for a particular update actual sequence of events would look like this
```
manager->downloader->manager->storage->manager->updater->storage->updater
```

then something has obviously go wrong.

The secure update example has own security monitor, which can deal with such problems, but if we want to imitate some behaviour and implement several test cases (with positive and negative scenarios) then this Kafka events analyzer (KEA) can be useful: it will be checking events sequences and if it knows in advance what to expect, it will raise error messages if e.g. instead of a negative scenario happened or vice versa.

In other words, KEA is there to support test automation.

## Implementation details

KEA contains the following modules

| Name | Purpose | Comment |
|----|----|----|
|*Analyzer* | entry point, initialization of the tool | |
|*Consumer_kea* | analyzes KEA own messages (e.g. self-test) |  
|*Consumer_monitor* | analyzes (security) monitor topic | gets same events as the security monitor, contains sequence verification logic
|*Consumer* | basic class for Kafka events consumers | 
|*Producer* | implements messages publishing functionality | currently used for self-test only

### Dependencies

KEA relies on the [sequence checker](https://github.com/sergey-sobolev/sequence_checker) implementation: when a sequence of events is accumulated KEA calls the checker binary with some arguments and evaluates return code.

## Configuration and running

The following arguments are supported by KEA
| Name | Purpose | Comment |
|----|----|----|
|*config_file*| Kafka configuration | positional argument, should be first - pathname to the configuration file, e.g. ../config.ini
|*--reset*| read Kafka topic from the beginning |
|*--states_def*| states definitions file name | used for the sequence checker, basically container services' names. E.g. ../states.def
|*--expect*| file with expected sequence | e.g. ../expected.txt
|*--checker*| sequence checker binary pathname | e.g. ../sq_checker

### States definitions example (states.def)

The file content can be as simple as 
```
def verifier;
def updater;
def downloader;
def manager;
def storage;
```

### Expectation example (expected.txt)

```
// expect no failure
//allowed=manager->downloader->manager->storage->manager->verifier(2)->storage->verifier(1)->manager->updater->storage->updater->#;

// expect failure
allowed=manager->downloader->manager->storage->manager->verifier(2)->storage->verifier(2)->manager->#;

// allow transmission faults 
//allowed=manager->downloader->manager->storage->manager->verifier(2)->storage->[verifier(1)->manager->updater->storage->updater]|[verifier(2)->manager]->#;
```

*Note*: The syntax of expected sequences definition see [here](https://github.com/sergey-sobolev/sequence_checker#node-parameter)

### Kafka configuration (config.ini)

```
[default]
bootstrap.servers=localhost:9092
# 'auto.offset.reset=earliest' to start reading from the beginning of
# the topic if no committed offsets exist.
auto.offset.reset=earliest

[analyzer]
group.id=analyzer
```

### Running the analyzer

There are two main options 
- run locally (requires environment setup) - do it if you want to change and debug code
- run in a docker container - do it if you only need to run the existing code and only modify sequences definitions

#### Local runtime environment

- sequence checker binary (the existing one is for Linux) - should be executable 
- python (3.8 or 3.10) with packages from requirements.txt installed (feel free to use `make prepare` command to setup a virtual environment)
- check if the config.ini file - make sure that the hostname of the broker is either localhost or in your /etc/hosts create an alias for the broker name, otherwise the analyzer will not be able to connect
- then run the analyzer using `make run-analyzer`  

#### Docker container

1. build kea image (execute `make image` in the project folder)
2. run the container (execute `make run`). 
 
Note, the local files *states.def* and *expected.txt* will be mapped to the container filesystem and the analyzer will use them, so to modify expected events simply change the local *expected.txt* file, the analyzer will apply changes on the fly.

### VSCode debug session configuration

In VS Code create new launch configuration and paste the following:
```
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Kea",
            "type": "python",
            "request": "launch",
            "program": "analyzer.py",
            "console": "integratedTerminal",
            "justMyCode": true,
            "args": ["../config.ini",
            "--states_def", "../states.def",
            "--expect", "../expected.txt",
            "--checker", "../sq_checker",
            //, "--reset"
        ],
            "cwd": "${workspaceFolder}/kea"
        }
    ]
}
```

## Support

Still have questions? Send me an email to sergey.sobolev@outlook.com