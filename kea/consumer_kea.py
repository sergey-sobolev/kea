from uuid import uuid4
from consumer import EventsConsumer
from producer import proceed_to_deliver


class KeaEventsConsumer(EventsConsumer):

    def __init__(self, topic=None) -> None:
        if topic is None:
            topic = "kea"
        super().__init__(topic)
        self.operations = {}
        self._self_test_req_id = None
        self._send_self_test_request()

    def _send_self_test_request(self):
        req_id = uuid4().__str__()
        self._self_test_req_id = req_id
        details = {
            "id": req_id,
            "operation": "self_test",
            "deliver_to": self.topic
        }
        proceed_to_deliver(id=req_id, details=details)

    def handle_event(self, id, details):
        # print(f"[debug][KEA] handling event {id}, {details}")
        # print(f"[info] handling event {id}, {details['source']}->{details['deliver_to']}: {details['operation']}")
        if id != self._self_test_req_id:
            print(
                f"[error] self test failed! unexpected event id {id} received! Expected id: {self._self_test_req_id}\n{details}")
        else:
            print(
                "[info] self test passed, communication with the message broker established")


if __name__ == '__main__':
    kea_ec = KeaEventsConsumer(topic="kea")
    kea_ec.start_consumer(args=None, config=None)
