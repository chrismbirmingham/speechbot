import deepspeech
import os
import time
import sounddevice
from tts_example import Speaker
from stt_example import Transcriber
from rasa_example import send_to_rasa


MODEL_FILE_PATH = os.path.join('models', 'deepspeech-0.9.3-models.pbmm')

PLAY_SPEED = 1.2

spkr = Speaker()
scribe = Transcriber(deepspeech.Model(MODEL_FILE_PATH))

starter_text = "Hi there!"

_, _, _, umm_wav = spkr.tts("umm")
_, _, _, wav = spkr.tts(starter_text)

sounddevice.play(wav, 22040 * PLAY_SPEED, blocking=True)
time.sleep(0.5)
scribe.listen()

while scribe.stream.is_active():
    if scribe.final_text:

        # Stop stream while playing audio
        scribe.stream.stop_stream()
        sounddevice.play(umm_wav, 22040 * PLAY_SPEED, blocking=False)
        print(f"Logging. Heard: {scribe.final_text}")

        response_text = send_to_rasa(scribe.final_text)
        print(f"Logging. Bot Response: {response_text}")

        _, _, _, wav = spkr.tts(response_text)
        sounddevice.play(wav, 22040 * PLAY_SPEED, blocking=True)

        print("Logging. Restarting the stream.")
        scribe.stream.start_stream()
        scribe.final_text = None

    time.sleep(0.005)

print("Woops - broke the loop. Goodbye")
