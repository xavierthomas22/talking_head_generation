import argparse
from TTS.api import TTS
import wave
import sys
import json
from vosk import Model, KaldiRecognizer, SetLogLevel

from talking_head_generation.AVCT.generate_talking_head import talking_head_generator

def text_from_chatgpt(args):
    text = "Hi! This is a test. I hope I do well! I will narrate a stroy now."
    return text

def create_audio_file(text, args):
    # Code for TTS here
    # model_name = TTS.list_models()[6]
    # print(model_name)
    # tts = TTS(model_name)
    # tts.tts_to_file(text=text, file_path="output.wav")
    args.audio_path = "output.wav"
    print('audio file created')

def create_phoneme_file(text, args):

    # Code for TTS here
    print(text)
    # You can set log level to -1 to disable debug messages
    SetLogLevel(0)

    wf = wave.open(args.audio_path, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        print("Audio file must be WAV format mono PCM.")

    model = Model(lang="en-us")

    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)

    phoneme = []

    while True:
        data = wf.readframes(1000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            # print(rec.Result())
            a = json.loads(rec.Result())["result"]

    print(a)
    exit()

    d = {}
    with open("talking_head_generation/AVCT/cmudict/cmudict.dict") as f:
        for line in f:
            l = line.split()
            key = l[0]
            val = l[1:]
            d[key] = val
    cmu_dict = d

    for idx, i in enumerate(a):
        i["end"] *= 100
        i["start"] *= 100
        i["end"] = int(i["end"])
        i["start"] = int(i["start"]) 

    if a[0]["start"] != 0:
        d = {}
        d["word"] = "sil"
        d["phones"] = [
            {
                "ph": "SIL",
                "bg": 0,
                "ed": a[0]["start"]
            }
        ]
        phoneme.append(d)

    for idx, i in enumerate(a):


        d = {}
        d["word"] = i['word']
        temp = cmu_dict[d["word"]]
        num_phones = len(temp)
        time_bw_phones = int((i["end"] - i["start"])/num_phones)
        d["phones"] = []



        for c in range(len(temp)):

            temp[c] = ''.join([i for i in temp[c] if not i.isdigit()])

            if c != len(temp)-1:

                d["phones"].append({"ph": temp[c], "bg": i["start"], "ed": i["start"]+time_bw_phones})
                i["start"] = i["start"]+time_bw_phones

            else:
                d["phones"].append({"ph": temp[c], "bg": i["start"], "ed": i["end"]})
            

        phoneme.append(d)

        if idx < len(a) - 1 and idx>0:
            i_1 = a[idx+1]
            if i["end"] != i_1["start"]:
                    d = {}
                    d["word"] = "sil"
                    d["phones"] = [
                        {
                            "ph": "SIL",
                            "bg": i["end"],
                            "ed": i_1["start"]
                        }
                    ]
                    phoneme.append(d)
        



    data = json.dumps(phoneme, indent = 4)


    with open('phoneme_final.json', 'w') as f:
        f.write(data)
    
    print('phoneme file created')

def talking_head_generation(args):
    generator = talking_head_generator(args)
    generator.generate_talking_head()
    print('talking head generated')


def gen_talking_head(args):
    text = text_from_chatgpt(args)
    create_audio_file(text, args)
    create_phoneme_file(text, args)
    exit()
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