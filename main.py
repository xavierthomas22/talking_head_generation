import argparse
from talking_head_generation.AVCT.generate_talking_head import talking_head_generator

def text_from_chatgpt(args):
    text = "Hi, this is a test!"
    return text

def create_audio_file(text, args):
    # Code for TTS here
    print('audio file created')

def talking_head_generation(args):
    generator = talking_head_generator(args)
    generator.generate_talking_head()
    print('talking head generated')


def gen_talking_head(args):
    text = text_from_chatgpt(args)
    create_audio_file(text, args)
    talking_head_generation(args)
    exit()

if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--prompt", type=str, default="story about a dog", help="Input prompt for ChatGPT")
    argparser.add_argument("--img_path", type=str, default=None, help="Single Input image of the Avatar", required=True)
    argparser.add_argument("--phoneme_path", type=str, default=None, help="Single Input image of the Avatar", required=True)
    argparser.add_argument("--audio_path", type=str, default=None, help="Single Input image of the Avatar", required=True)
    argparser.add_argument("--save_dir", type=str, default=None, help="Single Input image of the Avatar", required=True)
    args = argparser.parse_args()

    gen_talking_head(args)

# python main.py --img_path  /home/xavier.thomas/projects/AAAI22-one-shot-talking-face/samples/imgs/test_woman.jpg --audio_path /home/xavier.thomas/projects/AAAI22-one-shot-talking-face/samples/audios/obama2.wav --phoneme_path /home/xavier.thomas/projects/AAAI22-one-shot-talking-face/phoneme_final.json --save_dir outputs