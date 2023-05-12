class Communication:
    def __init__(self):
        self.protocol = None


class Message:
    def __init__(self):
        self.sender = None
        self.receiver = None
        self.content = None

    def set_sender(self, sender):
        self.sender = sender

    def set_receiver(self, receiver):
        self.receiver = receiver

    def set_content(self, content):
        self.content = content


class Protocol:
    def __init__(self):
        self.name = None
        self.message = None

    def set_name(self, name):
        self.name = name

    def set_message(self, message):
        self.message = message

    def send(self):
        raise NotImplementedError()

    def receive(self):
        raise NotImplementedError()

    def broadcast(self):
        raise NotImplementedError()


class MessageQueue:
    def __init__(self):
        self.queue = []

    def add_message(self, message):
        self.queue.append(message)

    def get_message(self):
        return self.queue.pop(0)

    def is_empty(self):
        return len(self.queue) == 0
