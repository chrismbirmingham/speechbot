from TTS.vocoder.utils.generic_utils import setup_generator
import torch
import time

from TTS.utils.generic_utils import setup_model
from TTS.utils.io import load_config
from TTS.utils.text.symbols import symbols, phonemes
from TTS.utils.audio import AudioProcessor
from TTS.utils.synthesis import synthesis

import sounddevice as sd

# model paths
TTS_MODEL = "content/tts_model.pth.tar"
TTS_CONFIG = "content/config.json"
VOCODER_MODEL = "content/vocoder_model.pth.tar"
VOCODER_CONFIG = "content/config_vocoder.json"


class Speaker:
    def __init__(self, use_cuda=False, verbose=False):
        self.use_cuda = use_cuda
        self.verbose = verbose

        # load configs
        self.TTS_CONFIG = load_config(TTS_CONFIG)
        self.VOCODER_CONFIG = load_config(VOCODER_CONFIG)

        # load the audio processor
        self.ap = AudioProcessor(**self.TTS_CONFIG.audio)

        # LOAD TTS MODEL
        self.speaker_id = None
        speakers = []

        # load the model
        num_chars = len(phonemes) if self.TTS_CONFIG.use_phonemes else len(symbols)
        self.model = setup_model(num_chars, len(speakers), self.TTS_CONFIG)

        # load model state
        cp = torch.load(TTS_MODEL, map_location=torch.device('cpu'))

        # load the model
        self.model.load_state_dict(cp['model'])
        if self.use_cuda:
            self.model.cuda()
        self.model.eval()

        # set model stepsize
        if 'r' in cp:
            self.model.decoder.set_r(cp['r'])

        # LOAD VOCODER MODEL
        self.vocoder_model = setup_generator(self.VOCODER_CONFIG)
        self.vocoder_model.load_state_dict(torch.load(VOCODER_MODEL, map_location="cpu")["model"])
        self.vocoder_model.remove_weight_norm()
        self.vocoder_model.inference_padding = 0

        ap_vocoder = AudioProcessor(**self.VOCODER_CONFIG['audio'])
        if self.use_cuda:
            self.vocoder_model.cuda()

        self.vocoder_model.eval()

    def tts(self, text, use_gl=False):
        t_1 = time.time()
        waveform, alignment, mel_spec, mel_postnet_spec, stop_tokens, inputs = synthesis(self.model, text, self.TTS_CONFIG, self.use_cuda, self.ap, self.speaker_id, style_wav=None,
                                                                                         truncated=False, enable_eos_bos_chars=self.TTS_CONFIG.enable_eos_bos_chars)
        # mel_postnet_spec = self.ap._denormalize(mel_postnet_spec.T)
        if not use_gl:
            waveform = self.vocoder_model.inference(torch.FloatTensor(mel_postnet_spec.T).unsqueeze(0))
            waveform = waveform.flatten()
        if self.use_cuda:
            waveform = waveform.cpu()
        waveform = waveform.numpy()
        rtf = (time.time() - t_1) / (len(waveform) / self.ap.sample_rate)
        tps = (time.time() - t_1) / len(waveform)
        if self.verbose:
            print(" > Run-time: {}".format(time.time() - t_1))
            print(" > Real-time factor: {}".format(rtf))
            print(" > Time per step: {}".format(tps))
        return alignment, mel_postnet_spec, stop_tokens, waveform


if __name__ == '__main__':
    SP = Speaker()
    speedup = 1.1
    sentence = "Hello world. Great to finally find my voice."
    align, spec, stop_tokens, wav = SP.tts(sentence)
    sd.play(wav, 22050 * speedup, blocking=True)
