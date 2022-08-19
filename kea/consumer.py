# implements Kafka topic consumer functionality


import threading
from confluent_kafka import Consumer, OFFSET_BEGINNING
import json


class EventsConsumer:
    def __init__(self, topic=None) -> None:
        self.topic = topic
        self._consumer = None

    def handle_event(self, id, details):
        # print(f"[debug] handling event {id}, {details}")
        # print(f"[info] handling event {id}, {details['source']}->{details['deliver_to']}: {details['operation']}")
        print(
            f"[debug] received event with id {id}. Note, this is a dummy callback and is supposed to be overloaded")

    def consumer_job(self, args, config, topic):
        # Create Consumer instance
        self._consumer = Consumer(config)

        # Set up a callback to handle the '--reset' flag.
        def reset_offset(consumer, partitions):
            if args.reset:
                print(f"[debug] resetting reading order for {consumer}")
                for p in partitions:
                    p.offset = OFFSET_BEGINNING
                consumer.assign(partitions)

        # Subscribe to topic
        self._consumer.subscribe([topic], on_assign=reset_offset)

        # Poll for new messages from Kafka and print them.
        try:
            while True:
                msg = self._consumer.poll(1.0)
                if msg is None:
                    # Initial message consumption may take up to
                    # `session.timeout.ms` for the consumer group to
                    # rebalance and start consuming
                    # print("Waiting...")
                    pass
                elif msg.error():
                    print(f"[error] {msg.error()}")
                else:
                    # Extract the (optional) key and value, and print.
                    try:
                        id = msg.key().decode('utf-8')
                        details_str = msg.value().decode('utf-8')
                        # print("[debug] consumed event from topic {topic}: key = {key:12} value = {value:12}".format(
                        #     topic=msg.topic(), key=id, value=details_str))
                        self.handle_event(id, json.loads(details_str))
                    except Exception as e:
                        print(
                            f"[error] malformed event received from topic {topic}: {msg.value()}. {e}")
        except KeyboardInterrupt:
            pass
        finally:
            # Leave group and commit final offsets
            self._consumer.close()

    def start_consumer(self, args, config, topic=None):
        if topic is not None:
            self.topic = topic
        if self.topic is None:
            raise BaseException("Topic name must not be empty!")
        threading.Thread(target=lambda: self.consumer_job(
            args, config, self.topic)).start()


if __name__ == '__main__':
    consumer = EventsConsumer()
    consumer.start_consumer(args=None, config=None, topic=None)
