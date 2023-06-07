class Message:
    def __init__(self, sender_id: int, receiver_id: int):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.payload = payload

    def get_content(self):
        return self.payload

    def get_sender(self) -> int:
        return self.sender_id


class MapUpdateMessage(Message):
    def __init__(self, sender_id: int, receiver_id: int, map_subset: np.array):
        super().__init__(sender_id, receiver_id)
        self.map_subset = map_subset

    def get_map_subset(self) -> np.array:
        return self.map_subset


class EnergyAndSeedLevelsStatusMessage(Message):
    def __init__(self, sender_id: int, receiver_id: int, status: Tuple[int, int]):
        super().__init__(sender_id, receiver_id)
        self.status = status

    def get_status(self) -> Tuple[int, int]:
        return self.status
