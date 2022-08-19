from consumer import EventsConsumer


class MonitorEventsConsumer(EventsConsumer):
    def __init__(self, topic=None) -> None:
        if topic is None:
            topic = "monitor"
        super().__init__(topic)
        self.operations = {}

    def handle_event(self, id, details):    
        # print(f"[debug][MEC] handling event {id}")
        # print(f"[debug][MEC] handling event {id}, {details}")
        # print(f"[info] handling event {id}, {details['source']}->{details['deliver_to']}: {details['operation']}")
        self.parse_operation(id, details)

    def dump_sequence(self, operations):
        seq = "$->"
        source = None
        for event in operations:
            if source is None or source != event["source"]:
                seq += event["source"] + "->" + event["deliver_to"]
            else:
                seq += "->" + event["deliver_to"]
            source = event["deliver_to"]
        return seq + "->#"

    def parse_operation(self, id, details):
        if id in self.operations:
            self.operations[id].append(details)
            print(f"accumulated sequence: {self.dump_sequence(self.operations[id])}")
        else:
            self.operations[id] = [details]
            print(f"started new sequence: {self.dump_sequence(self.operations[id])}")


if __name__ == '__main__':
    mec = MonitorEventsConsumer(topic="monitor")
    mec.start_consumer(args=None, config=None, topic=None)
