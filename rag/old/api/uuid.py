import uuid

class UniqueDictionary:
    def __init__(self):
        self.dictionary = {}

    def generate_unique_key(self):
        key = str(uuid.uuid4())
        while key in self.dictionary:
            key = str(uuid.uuid4())
        return key

    def add_element(self, value):
        key = self.generate_unique_key()
        self.dictionary[key] = value
        return {key: value}

    def remove_value(self, value):
        keys_to_remove = []
        for key, val in self.dictionary.items():
            if val == value:
                keys_to_remove.append(key)
        for key in keys_to_remove:
            del self.dictionary[key]


# unique_dict = UniqueDictionary()

# element = unique_dict.add_element("value1")
# print(element)  # 输出：{'79b7a9d1-05e7-4d10-97a0-8c91a335192d': 'value1'}

# element = unique_dict.add_element("value2")
# print(element)  # 输出：{'8e5e0e63-7b2f-47d1-b195-71ff4d6d1304': 'value2'}

# print(unique_dict.dictionary)  # 输出：{'79b7a9d1-05e7-4d10-97a0-8c91a335192d': 'value1', '8e5e0e63-7b2f-47d1-b195-71ff4d6d1304': 'value2'}
