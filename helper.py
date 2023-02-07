import wave
import sys
import json
import subprocess
from vosk import Model, KaldiRecognizer, SetLogLevel


def create_phoneme_file(args, temp_path=None):

    if temp_path:
        audio_path = temp_path
        tts = True
    else:
        audio_path = args.audio_path    
        tts = False

    SAMPLE_RATE = 16000
    WORDS_PER_LINE = 7

    SetLogLevel(0)

    model = Model(lang="en-us")
    rec = KaldiRecognizer(model, SAMPLE_RATE)
    rec.SetWords(True)

    command = ["ffmpeg", "-nostdin", "-loglevel", "quiet", "-i", audio_path,
               "-ar", str(SAMPLE_RATE), "-ac", "1", "-f", "s16le", "-"]
    with subprocess.Popen(command, stdout=subprocess.PIPE) as process:

        results = []
        while True:
            data = process.stdout.read(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                results.append(rec.Result())
        results.append(rec.FinalResult())

    d = {}
    with open("talking_head_generation/AVCT/cmudict/cmudict.dict") as f:
        for line in f:
            l = line.split()
            key = l[0]
            val = l[1:]
            d[key] = val
    cmu_dict = d

    phoneme = []

    for k, r in enumerate(results):
        a = json.loads(r).get("result")
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
            
            if tts: # If TTS added Silence to the end of the video, s that video does not abruptly cut off.
                if k == len(results) - 1 and  idx == len(a) - 1:
                    d = {}
                    d["word"] = "sil"
                    d["phones"] = [
                        {
                            "ph": "SIL",
                            "bg": i["end"],
                            "ed": i["end"] + 100
                        }
                    ]
                    phoneme.append(d)


    data = json.dumps(phoneme, indent = 4)


    with open(f'{args.save_dir}/phoneme.json', 'w') as f:
        f.write(data)

