from pygame import key
from key_map import KEY_MAP

class Keyboard:
    def __init__(self, key_mapping=KEY_MAP) -> None:
        self.key_mapping = key_mapping

    def is_pressed(self, key_val: int) -> bool:
        """
        Return whether the key corresponding to key_val is being pressed.
        """
        return key.is_pressed[self.key_mapping[key_val]]
    
    def is_any_pressed(self) -> int:
        """
        Return None if no key is being pressed, otherwise return the value of
        the key.
        """
        for key_val in self.key_mapping:
            if key.get_pressed(self.key_mapping[key_val]):
                return key_val
        
        return None