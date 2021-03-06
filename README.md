# speechbot
A local, interactive, speech-based chatbot with Rasa and Mozilla Deepspeech/TTS

This was heavily inspired by the excellent example from Rasa [here](https://blog.rasa.com/how-to-build-a-voice-assistant-with-open-source-rasa-and-mozilla-tools/), the TTS colab [here](https://colab.research.google.com/drive/1tKHSI20kRlOL0PSA8mCVJQIrgRIswg0F?usp=sharing#scrollTo=ofPCvPyjZEcT) and the deepspeech docs [here](https://deepspeech.readthedocs.io/en/v0.9.3/?badge=latest)


# Getting started
To set up speechbot:

```
pip install -r requirments.txt
sh setup_stt.sh
sh setup_tts.sh
```

Note: if PyAudio is having trouble installing, try `sudo apt install portaudio19-dev python3-pyaudio`

Once setup is complete, the example scripts should work. To run the rasa example you will need to start one of the rasa bots, which can be done by entering the rasa_[bot] directory and calling `$rasa run`. I recommend starting with the rasa_example, as rasa_greeter is still a work in progress.

# Add your own bot
To add a new bot, you just have to copy the custom_channel.py into your bot's addons directory, and copy the following into the credentials.yml:

```
addons.custom_channel.MyIO:
  username: "user_name"
  another_parameter: "some value"
```

To converse with this bot, you will need to `rasa train` and `rasa run` in the bot's directory and launch speechbot_example.py or rasa_example.py (if you don't want to use your voice).


# Contributing
Todo:
- [ ] Debugging threading issues
- [ ] Simplifying use of TTS library (is there a pip package?)
- [ ] Setting up alternate voice models