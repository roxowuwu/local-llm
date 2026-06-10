from abc import ABC, abstractmethod


# -----------------------------
# Base (Abstract)
# -----------------------------
class BaseInputLayer(ABC):

    @abstractmethod
    def get(self) -> str:
        pass


# -----------------------------
# Text Input
# -----------------------------
class TextInputLayer(BaseInputLayer):

    def __init__(self, prompt=">> "):
        self.prompt = prompt

    def get(self) -> str:
        try:
            user_input = input(self.prompt)
            return user_input.strip()
        except KeyboardInterrupt:
            return "exit"


# -----------------------------
# Voice Input (STUB)
# -----------------------------
class VoiceInputLayer(BaseInputLayer):

    def __init__(self):
        pass

    def listen(self) -> str:
        # future: integrate whisper / vosk
        return "voice input not implemented"

    def get(self) -> str:
        return self.listen()


# -----------------------------
# Factory Function
# -----------------------------
def get_input_layer(mode: str) -> BaseInputLayer:
    mode = mode.lower()

    if mode == "voice":
        return VoiceInputLayer()
    else:
        return TextInputLayer()
