import os
from consumer import EventsConsumer
import subprocess

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
        seq = ""
        source = None
        for event in operations:
            src = event["source"]
            dst = event["deliver_to"]
            verification_status = ""
            if src == 'verifier':
                verification_status = '(0)' if event['verified'] is True else '(1)'
            if source is None or source != event["source"]:
                seq += src + verification_status + "->" + dst
            else:
                seq += verification_status + "->" + dst
            source = dst
        return seq

    def call_external_checker(self, id, sequence):
        expected = ""
        if self.args.expect is not None:
            self.args.expect.seek(0)  # read the file from the beginning
            expected = self.args.expect.read()

        if 'kea->kea' in sequence:
            print("[info] skipping internal self-test sequence")
        else:
            seq = expected + "\nexecuted=" + sequence + ";" # add line break to exit previously commented line, if any
            seq_file_name = id + ".seq"
            with open(seq_file_name, "w") as f:
                f.write(seq)
            f.close()
            result = "invalid"
            with open(seq_file_name, "r") as f:
                try:
                    completed_process = subprocess.run([self.args.checker, '-cfg', self.args.states_def], stdin=f, check=True)
                    result = 'ok' if completed_process.returncode == 0 else 'invalid'
                except Exception as e:
                    print(f"[error] sequence checker failed: {e}")
                    pass
            f.close()
            os.remove(seq_file_name)  # remove the temp file
            print(f"[info] executed the checker {self.args.checker} with definitions from {self.args.states_def} and\n"
                f"expectations\n{expected}\nagainst the sequence\n{sequence}\n"
                f"the result is: {result}")
            if result == "invalid":
                # print(f"[error] executed the checker {self.args.checker} with definitions from {self.args.states_def} and\n"
                #     f"expectations\n{expected}\nagainst the sequence\n{sequence}\n"
                #     "the result is: invalid")
                print("[error] sequence invalid")
            else:
                print("[info] sequence valid")

    def parse_operation(self, id, details):
        if id in self.operations:
            self.operations[id].append(details)
            seq = self.dump_sequence(self.operations[id])
            print(f"[info] accumulated sequence: {seq}")
        else:
            self.operations[id] = [details]
            seq = self.dump_sequence(self.operations[id])
            print(f"[info] new sequence: {seq}")
        if self.args.checker is not None:
            self.call_external_checker(id=id, sequence=seq)

if __name__ == '__main__':
    mec = MonitorEventsConsumer(topic="monitor")
    mec.start_consumer(args=None, config=None, topic=None)
