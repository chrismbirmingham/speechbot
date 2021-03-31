import sounddevice
import deepspeech
import os
import time
from tts_example import Speaker
from stt_example import Transcriber


USE_CUDA = False
MODEL_FILE_PATH = os.path.join('models', 'deepspeech-0.9.3-models.pbmm')

SP = Speaker()
LI = Transcriber(deepspeech.Model(MODEL_FILE_PATH))

prepend_text = "What I heard you say was "
starter_text = "Hi there! What do you want to talk about?"

_, _, _, umm_wav = SP.tts("umm")
_, _, _, wav = SP.tts(starter_text)

sounddevice.play(wav, 24050, blocking=True)
time.sleep(0.5)
LI.listen()

while LI.stream.is_active():
    if LI.final_text:

        LI.stream.stop_stream()
        sounddevice.play(umm_wav, 24050, blocking=False)

        print(prepend_text + LI.final_text)

        _, _, _, wav = SP.tts(prepend_text + LI.final_text)
        sounddevice.play(wav, 24050, blocking=True)

        print("Restarting the stream")
        LI.stream.start_stream()

        LI.final_text = None
    time.sleep(0.005)
print("whoops - broke the loop")
