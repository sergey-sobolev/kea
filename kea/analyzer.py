#!/usr/bin/env python

from argparse import ArgumentParser, FileType
from configparser import ConfigParser
from consumer_kea import KeaEventsConsumer
from consumer_monitor import MonitorEventsConsumer
from producer import start_producer
from multiprocessing import Queue

if __name__ == '__main__':
    # Parse the command line.
    parser = ArgumentParser()
    parser.add_argument('config_file', type=FileType('r'))
    parser.add_argument('--reset', action='store_true')
    args = parser.parse_args()

    # Parse the configuration.
    # See https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md
    config_parser = ConfigParser()
    config_parser.read_file(args.config_file)
    config = dict(config_parser['default'])
    config.update(config_parser['analyzer'])
    
    requests_queue = Queue()
    start_producer(args, config, requests_queue)    

    
    kea_ec = KeaEventsConsumer()
    monitor_ec = MonitorEventsConsumer()

    monitor_ec.start_consumer(args, config)
    kea_ec.start_consumer(args, config)

