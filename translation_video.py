#!/usr/bin/env python3.7

# coding=utf8
from gtts import gTTS
import gradio as gr
import os, datetime
import speech_recognition as sr
from googletrans import Translator, constants
from pprint import pprint
from moviepy.editor import *
from pydub import AudioSegment
from pydub.silence import split_on_silence
import soundfile as sf
import ffmpeg

import argparse
from pathlib import Path

def parser():
    parse = argparse.ArgumentParser("Transltation video text")

    parse.add_argument("--source"  , type=str, help="source mp4 video", required=True)
    parse.add_argument("--out_file", type=str, help="Translated file", default="")
    return parse

def get_large_audio_transcription(path2):

  tmp_str_trans = str_trans = str_source = ""

  ed_time = st_time = 0.000001
  translator = Translator()

  r = sr.Recognizer()
  sound = AudioSegment.from_wav(path2)

  chunks = split_on_silence(sound,
    min_silence_len = 500,
    silence_thresh = sound.dBFS-14,
    keep_silence=500,
  )


  for i, audio_chunk in enumerate(chunks, start=1):
    chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
    audio_chunk.export(chunk_filename, format="wav")
    with sr.AudioFile(chunk_filename) as source:
      audio_listened = r.record(source)

      f = sf.SoundFile( chunk_filename )
      ed_time += (f.frames / f.samplerate)

      try:
        text = r.recognize_google(audio_listened)
      except sr.UnknownValueError as e:
        print("Error:", str(e))
        pass
      else:
        text = f"{text.capitalize()}. "

        date_st = str( datetime.timedelta(seconds=st_time) ).replace(".",",")[0:-3]
        date_ed = str( datetime.timedelta(seconds=ed_time) ).replace(".",",")[0:-3]

        str_source += f"{i}\n{date_st} --> {date_ed}\n{text}\n\n"

        translation = translator.translate(text, dest='ko')
        str_trans += f"{i}\n{date_st} --> {date_ed}\n{translation.text}\n\n"

        print(chunk_filename, ":", text)
        print(chunk_filename, ":", translation.text)
        print( datetime.timedelta(seconds=(f.frames / f.samplerate)))

    st_time += (f.frames / f.samplerate)

    tmp_str_trans += text

  return str_source, str_trans

if __name__ == '__main__':
  args = parser().parse_args()

  folder_name = "build"
  if os.path.isdir(folder_name):
    import shutil
    shutil.rmtree(folder_name, ignore_errors=True)
  os.mkdir(folder_name)

  print(args.source.replace("!TM_","\ "))

  videoclip = VideoFileClip(args.source.replace("!TM_"," "))
  videoclip.audio.write_audiofile("build/test.wav",codec='pcm_s16le')

  str_source, str_trans = get_large_audio_transcription("build/test.wav")


  if not os.path.isdir("build_trans"):
    os.makedirs("build_trans")
  output_file_name = str(args.source).split("/")[-1].replace("\ ","")
  with open(f"build_trans/{output_file_name}_en.txt.srt".replace(" ",""),'w') as f_s:
    f_s.write(str_source)
  with open(f"build_trans/{output_file_name}_ko.txt.srt".replace(" ",""),'w') as f_o:
    f_o.write(str_trans)

  if not os.path.isdir("build_video"):
    os.makedirs("build_video")
  video = ffmpeg.input(args.source.replace("!TM_"," "))
  audio = video.audio
  ffmpeg.concat(video.filter("subtitles", f"build_trans/{output_file_name}_en.txt.srt"), audio, v=1, a=1).output(f"build_video/{output_file_name}_en.mp4".replace(" ","")).run()
  ffmpeg.concat(video.filter("subtitles", f"build_trans/{output_file_name}_ko.txt.srt"), audio, v=1, a=1).output(f"build_video/{output_file_name}_ko.mp4".replace(" ","")).run()
