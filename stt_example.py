
import deepspeech
import numpy as np
import os
import pyaudio
import time

# Cuda for deepspeech is controlled at the pip package level
# pip install deepspeech-gpu

# DeepSpeech parameters
BEAM_WIDTH = 700
LM_ALPHA = 0.75
LM_BETA = 1.85

MODEL_FILE_PATH = os.path.join('models', 'deepspeech-0.9.3-models.pbmm')
SCORER_PATH = os.path.join('models', 'deepspeech-0.9.3-models.scorer')


class Transcriber:
    def __init__(self, model):
        self.model = model
        self.model.enableExternalScorer(SCORER_PATH)
        self.model.setScorerAlphaBeta(LM_ALPHA, LM_BETA)
        self.model.setBeamWidth(BEAM_WIDTH)
        # self.model.enableDecoderWithLM(LM_FILE_PATH, TRIE_FILE_PATH, LM_ALPHA, LM_BETA)

        # Create a Streaming session
        self.ds_stream = self.model.createStream()

        # Encapsulate DeepSpeech audio feeding into a callback for PyAudio
        self.text_so_far = ''
        self.t_start = time.time()
        self.t_wait = .5
        self.final_text = None

    def process_audio(self, in_data, frame_count, time_info, status):
        data16 = np.frombuffer(in_data, dtype=np.int16)
        self.ds_stream.feedAudioContent(data16)
        text = self.ds_stream.intermediateDecode()
        try:
            if text != self.text_so_far:
                if text not in ["i ", "he ", "the "]:
                    print('Interim text = {};'.format(text))
                self.text_so_far = text
                self.t_start = time.time()
            elif text != '' and (time.time() - self.t_start > self.t_wait):
                if text not in ["i ", "he ", "the "]:
                    print("Finishing stream")
                    text = self.ds_stream.finishStream()
                    print('Final text = {}.\n'.format(text))
                    self.final_text = text
                    self.ds_stream = self.model.createStream()
        except Exception as e:
            print(f"Text: '{text}'; So far: '{self.text_so_far}")
            print(self.t_start)
            raise e
        return (in_data, pyaudio.paContinue)

    def listen(self):
        print("setting up to listen")
        # Feed audio to deepspeech in a callback to PyAudio
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=1024,
            stream_callback=self.process_audio
        )

        print('Please start speaking, when done press Ctrl-C ...')
        self.stream.start_stream()
        print("listening now")
        return


if __name__ == '__main__':
    # Make DeepSpeech Model
    model = deepspeech.Model(MODEL_FILE_PATH)
    stt = Transcriber(model)
    stt.listen()
    try:
        while stt.stream.is_active():
            time.sleep(0.05)
    except KeyboardInterrupt:
        # PyAudio
        stt.stream.stop_stream()
        stt.stream.close()
        stt.audio.terminate()
        print('Finished recording.')
