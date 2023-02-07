import argparse
from TTS.api import TTS
from helper import create_phoneme_file

from talking_head_generation.AVCT.generate_talking_head import talking_head_generator


def text_from_chatgpt(args):
    text = "Hey Guys, This demo looks pretty cool. Let's make this big."
    return text


def create_audio_file(text, args):
    # Code for TTS here: https://github.com/coqui-ai/TTS
    model_name = TTS.list_models()[0] # 11 - glow-tts trained on ljspeech
    tts = TTS(model_name)
    audio_path_temp = f'{args.save_dir}/temp.wav'
    tts.tts_to_file(text=text, speaker=tts.speakers[4], language=tts.languages[0], file_path=audio_path_temp)
    print('audio file created')
    return audio_path_temp


def talking_head_generation(args, audio_path_temp):
    generator = talking_head_generator(args)
    generator.generate_talking_head(audio_path_temp)
    print('talking head generated')


def gen_talking_head(args):
    if args.input == "text":
        text = text_from_chatgpt(args)
        audio_path_temp = create_audio_file(text, args)
    else:
        audio_path_temp = None
        if not args.audio_path:
            raise ValueError('Please provide an input path if not using audio input')
    create_phoneme_file(args, audio_path_temp)
    talking_head_generation(args, audio_path_temp)



if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--prompt", type=str, default="story about a dog", help="Input prompt for ChatGPT")
    argparser.add_argument("--img_path", type=str, default=None, help="Single Input image of the Avatar", required=True)
    argparser.add_argument("--save_dir", type=str, default=None, help="Single Input image of the Avatar", required=True)
    argparser.add_argument("--input", type=str, default="audio", help="audio/text", required=True)
    argparser.add_argument("--audio_path", type=str)
    args = argparser.parse_args()

    gen_talking_head(args)
