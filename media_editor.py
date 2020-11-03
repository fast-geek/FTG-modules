# requires: pydub
# requires: numpy
# requires: requests
from pydub import AudioSegment
from pydub import effects
from telethon import types
from .. import loader, utils
from pydub import AudioSegment
import io
import os
import requests
import numpy as np
import math

# Author: https://t.me/dekftgmodules and https://t.me/ftgmodulesbyfl1yd

def register(cb):
    cb(AudioEditorMod())


class AudioEditorMod(loader.Module):
    """AudioEditor"""
    strings = {'name': 'Audio and video editor'}

    def __init__(self):
        self.name = self.strings['name']
        self._me = None
        self._ratelimit = []

    async def client_ready(self, client, db):
        self._db = db
        self._client = client
        self.me = await client.get_me()

    async def basscmd(self, message):
        v = False
        accentuate_db = 2
        reply = await message.get_reply_message()
        if not reply:
            await message.edit("А где реплай?")
            return
        if utils.get_args_raw(message):
            ar = utils.get_args_raw(message)
            try:
                int(ar)
                if int(ar) >= 2 and int(ar) <= 100:
                    accentuate_db = int(ar)
                else:
                    await message.edit("Укажите уровень BassBoost'а от 2 до 100!")
                    return
            except Exception as exx:
                await message.edit("Неверный аргумент!<br>" + str(exx))
                return
        else:
            accentuate_db = 2
        await message.edit("Скачиваем...")
        fname = await message.client.download_media(message=reply.media)
        await message.edit("BassBoost'им...")
        if fname.endswith(".oga") or fname.endswith(".ogg"):
            v = True
            audio = AudioSegment.from_file(fname)
        elif fname.endswith(".mp3") or fname.endswith(".m4a") or fname.endswith(".wav"):
            audio = AudioSegment.from_file(fname)

        else:
            await message.edit("<b>Unsupported format!</b>")
            os.remove(fname)
            return
        sample_track = list(audio.get_array_of_samples())
        est_mean = np.mean(sample_track)
        est_std = 3 * np.std(sample_track) / (math.sqrt(2))
        bass_factor = int(round((est_std - est_mean) * 0.005))
        attenuate_db = 0
        filtered = audio.low_pass_filter(bass_factor)
        out = (audio - attenuate_db).overlay(filtered + accentuate_db)
        m = io.BytesIO()

        if v:
            m.name = "voice.ogg"
            out.split_to_mono()
            await message.edit("Экспортируем...")
            out.export(m, format="ogg", bitrate="64k", codec="libopus")
            await message.edit("Отправляем...")
            await message.client.send_file(message.to_id, m, reply_to=reply.id, voice_note=True)
        else:
            m.name = "BassBoosted.mp3"
            await message.edit("Экспортируем...")
            out.export(m, format="mp3")
            await message.edit("Отправляем...")
            await message.client.send_file(message.to_id, m, reply_to=reply.id, attributes=[
                types.DocumentAttributeAudio(duration=reply.document.attributes[0].duration,
                                             title=f"BassBoost {str(accentuate_db)}lvl", performer="BassBoost")])
        await message.delete()
        os.remove(fname)

    async def echoscmd(self, message):
        v = False
        reply = await message.get_reply_message()
        if not reply:
            await message.edit("А где реплай?")
            return
        await message.edit("Скачиваем...")
        fname = await message.client.download_media(message=reply.media)
        await message.edit("Echo'ярим...")
        if fname.endswith(".oga") or fname.endswith(".ogg"):
            v = True
            echo = AudioSegment.from_file(fname)
        elif fname.endswith(".mp3") or fname.endswith(".m4a") or fname.endswith(".wav"):
            echo = AudioSegment.from_file(fname)

        else:
            await message.edit("<b>Unsupported format!</b>")
            os.remove(fname)
            return
        out = AudioSegment.empty()
        n = 200
        if os.path.isfile("none.mp3") == False:
            open("none.mp3", "wb").write(
                requests.get("https://raw.githubusercontent.com/Daniel3k00/files-for-modules/master/none.mp3").content)
        out += echo + AudioSegment.from_file("none.mp3")
        for i in range(5):
            echo = echo - 7
            out = out.overlay(echo, n)
            n += 200
        m = io.BytesIO()
        await message.edit("Отправляем...")
        if v:
            m.name = "voice.ogg"
            out.split_to_mono()
            out.export(m, format="ogg", bitrate="64k", codec="libopus")
            await message.client.send_file(message.to_id, m, reply_to=reply.id, voice_note=True)
        else:
            m.name = "Echo.mp3"
            out.export(m, format="mp3")
            await message.client.send_file(message.to_id, m, reply_to=reply.id, attributes=[
                types.DocumentAttributeAudio(duration=reply.document.attributes[0].duration, title="Эхо эффект",
                                             performer="Эхо эффект")])
        await message.delete()
        os.remove(fname)
        os.remove("none.mp3")

    async def volupcmd(self, message):
        v = False
        reply = await message.get_reply_message()
        if not reply:
            await message.edit("А где реплай?")
            return
        await message.edit("Скачиваем...")
        fname = await message.client.download_media(message=reply.media)
        await message.edit("Vol'им...")
        if fname.endswith(".oga") or fname.endswith(".ogg"):
            v = True
            audio = AudioSegment.from_file(fname).apply_gain(+10)
        elif fname.endswith(".mp3") or fname.endswith(".m4a") or fname.endswith(".wav"):
            audio = AudioSegment.from_file(fname).apply_gain(+10)
        else:
            await message.edit("<b>Unsupported format!</b>")
            os.remove(fname)
            return
        m = io.BytesIO()
        await message.edit("Отправляем...")
        if v:
            m.name = "voice.ogg"
            audio.split_to_mono()
            audio.export(m, format="ogg", bitrate="64k", codec="libopus")
            await message.client.send_file(message.to_id, m, reply_to=reply.id, voice_note=True)
        else:
            m.name = "VolUp.mp3"
            audio.export(m, format="mp3")
            await message.client.send_file(message.to_id, m, reply_to=reply.id, attributes=[
                types.DocumentAttributeAudio(duration=reply.document.attributes[0].duration, title="VolUp",
                                             performer="VolUp")])
        await message.delete()
        os.remove(fname)

    async def voldwcmd(self, message):
        v = False
        reply = await message.get_reply_message()
        if not reply:
            await message.edit("А где реплай?")
            return
        await message.edit("Скачиваем...")
        fname = await message.client.download_media(message=reply.media)
        await message.edit("Vol'им...")
        if fname.endswith(".oga") or fname.endswith(".ogg"):
            v = True
            audio = AudioSegment.from_file(fname).apply_gain(-10)
        elif fname.endswith(".mp3") or fname.endswith(".m4a") or fname.endswith(".wav"):
            audio = AudioSegment.from_file(fname).apply_gain(-10)
        else:
            await message.edit("<b>Unsupported format!</b>")
            os.remove(fname)
            return
        m = io.BytesIO()
        await message.edit("Отправляем...")
        if v:
            m.name = "voice.ogg"
            audio.split_to_mono()
            audio.export(m, format="ogg", bitrate="64k", codec="libopus")
            await message.client.send_file(message.to_id, m, reply_to=reply.id, voice_note=True)
        else:
            m.name = "VolDown.mp3"
            audio.export(m, format="mp3")
            await message.client.send_file(message.to_id, m, reply_to=reply.id, attributes=[
                types.DocumentAttributeAudio(duration=reply.document.attributes[0].duration, title="VolDown",
                                             performer="VolDown")])
        await message.delete()
        os.remove(fname)

    async def revscmd(self, message):
        v = False
        reply = await message.get_reply_message()
        if not reply:
            await message.edit("А где реплай?")
            return
        await message.edit("Скачиваем...")
        fname = await message.client.download_media(message=reply.media)
        await message.edit("Reverse'им...")
        if fname.endswith(".oga") or fname.endswith(".ogg"):
            v = True
            audio = AudioSegment.from_file(fname)
        elif fname.endswith(".mp3") or fname.endswith(".m4a") or fname.endswith(".wav"):
            audio = AudioSegment.from_file(fname)
        else:
            await message.edit("<b>Unsupported format!</b>")
            os.remove(fname)
            return
        rev = audio.reverse()
        audio = rev
        m = io.BytesIO()
        await message.edit("Отправляем...")
        if v:
            m.name = "voice.ogg"
            audio.split_to_mono()
            audio.export(m, format="ogg", bitrate="64k", codec="libopus")
            await message.client.send_file(message.to_id, m, reply_to=reply.id, voice_note=True)
        else:
            m.name = "Reversed.mp3"
            audio.export(m, format="mp3")
            await message.client.send_file(message.to_id, m, reply_to=reply.id, attributes=[
                types.DocumentAttributeAudio(duration=reply.document.attributes[0].duration, title="Reversed",
                                             performer="Reversed")])
        await message.delete()
        os.remove(fname)

    async def repscmd(self, message):
        v = False
        reply = await message.get_reply_message()
        if not reply:
            await message.edit("А где реплай?")
            return
        await message.edit("Скачиваем...")
        fname = await message.client.download_media(message=reply.media)
        await message.edit("Repeat'им...")
        if fname.endswith(".oga") or fname.endswith(".ogg"):
            v = True
            audio = AudioSegment.from_file(fname)
        elif fname.endswith(".mp3") or fname.endswith(".m4a") or fname.endswith(".wav"):
            audio = AudioSegment.from_file(fname)
        else:
            await message.edit("<b>Unsupported format!</b>")
            os.remove(fname)
            return
        audio = audio * 2
        m = io.BytesIO()
        await message.edit("Отправляем...")
        if v:
            m.name = "voice.ogg"
            audio.split_to_mono()
            audio.export(m, format="ogg", bitrate="64k", codec="libopus")
            await message.client.send_file(message.to_id, m, reply_to=reply.id, voice_note=True)
        else:
            m.name = "Repeated.mp3"
            audio.export(m, format="mp3")
            await message.client.send_file(message.to_id, m, reply_to=reply.id, attributes=[
                types.DocumentAttributeAudio(duration=reply.document.attributes[0].duration, title="Repeated",
                                             performer="Repeated")])
        await message.delete()
        os.remove(fname)

    async def slowscmd(self, message):
        v = False
        reply = await message.get_reply_message()
        if not reply:
            await message.edit("А где реплай?")
            return
        await message.edit("Скачиваем...")
        fname = await message.client.download_media(message=reply.media)
        await message.edit("Замедляем...")
        if fname.endswith(".oga") or fname.endswith(".ogg"):
            v = True
            audio = AudioSegment.from_file(fname)
        elif fname.endswith(".mp3") or fname.endswith(".m4a") or fname.endswith(".wav"):
            audio = AudioSegment.from_file(fname)
        else:
            await message.edit("<b>Unsupported format!</b>")
            os.remove(fname)
            return
        sound = AudioSegment.from_file(fname)
        sound_with_altered_frame_rate = sound._spawn(sound.raw_data, overrides={
            "frame_rate": int(sound.frame_rate * 0.5)
        })
        sound = sound_with_altered_frame_rate.set_frame_rate(sound.frame_rate)
        await message.edit("Отправляем...")
        m = io.BytesIO()
        if v:
            m.name = "voice.ogg"
            audio.split_to_mono()
            sound.export(m, format="ogg", bitrate="64k", codec="libopus")
            await message.client.send_file(message.to_id, m, reply_to=reply.id, voice_note=True)
        else:
            m.name = "Slow.mp3"
            sound.export(m, format="mp3")
            await message.client.send_file(message.to_id, m, reply_to=reply.id, attributes=[
                types.DocumentAttributeAudio(duration=reply.document.attributes[0].duration, title="Slowed",
                                             performer="Slowed")])
        await message.delete()

    async def fastscmd(self, message):
        v = False
        reply = await message.get_reply_message()
        if not reply:
            await message.edit("А где реплай?")
            return
        await message.edit("Скачиваем...")
        fname = await message.client.download_media(message=reply.media)
        await message.edit("Ускоряем...")
        if fname.endswith(".oga") or fname.endswith(".ogg"):
            v = True
            audio = AudioSegment.from_file(fname)
        elif fname.endswith(".mp3") or fname.endswith(".m4a") or fname.endswith(".wav"):
            audio = AudioSegment.from_file(fname)
        else:
            await message.edit("<b>Unsupported format!</b>")
            os.remove(fname)
            return
        sound = AudioSegment.from_file(fname)
        sound_with_altered_frame_rate = sound._spawn(sound.raw_data, overrides={
            "frame_rate": int(sound.frame_rate * 1.5)
        })
        sound = sound_with_altered_frame_rate.set_frame_rate(sound.frame_rate)
        await message.edit("Отправляем...")
        m = io.BytesIO()
        if v:
            m.name = "voice.ogg"
            audio.split_to_mono()
            sound.export(m, format="ogg", bitrate="64k", codec="libopus")
            await message.client.send_file(message.to_id, m, reply_to=reply.id, voice_note=True)
        else:
            m.name = "Fast.mp3"
            sound.export(m, format="mp3")
            await message.client.send_file(message.to_id, m, reply_to=reply.id)
        await message.delete()

    async def leftscmd(self, message):
        v = False
        reply = await message.get_reply_message()
        if not reply:
            await message.edit("А где реплай?")
            return
        await message.edit("Скачиваем...")
        fname = await message.client.download_media(message=reply.media)
        await message.edit("Pan'им...")
        if fname.endswith(".oga") or fname.endswith(".ogg"):
            v = True
            sound = AudioSegment.from_file(fname)
        elif fname.endswith(".mp3") or fname.endswith(".m4a") or fname.endswith(".wav"):
            sound = AudioSegment.from_file(fname)
        else:
            await message.edit("<b>Unsupported format!</b>")
            os.remove(fname)
            return
        sound = AudioSegment.from_file(fname)
        sound = effects.pan(sound, -1.0)
        await message.edit("Отправляем...")
        m = io.BytesIO()
        if v:
            m.name = "voice.ogg"
            sound.export(m, format="ogg", bitrate="64k", codec="libopus")
            await message.client.send_file(message.to_id, m, reply_to=reply.id, voice_note=True)
        else:
            m.name = "Left.mp3"
            sound.export(m, format="mp3")
            await message.client.send_file(message.to_id, m, reply_to=reply.id, attributes=[
                types.DocumentAttributeAudio(duration=reply.document.attributes[0].duration, title="Fasted",
                                             performer="Fasted")])
        await message.delete()

    async def rightscmd(self, message):
        v = False
        reply = await message.get_reply_message()
        if not reply:
            await message.edit("А где реплай?")
            return
        await message.edit("Скачиваем...")
        fname = await message.client.download_media(message=reply.media)
        await message.edit("Pan'им...")
        if fname.endswith(".oga") or fname.endswith(".ogg"):
            v = True
            sound = AudioSegment.from_file(fname)
        elif fname.endswith(".mp3") or fname.endswith(".m4a") or fname.endswith(".wav"):
            sound = AudioSegment.from_file(fname)
        else:
            await message.edit("<b>Unsupported format!</b>")
            os.remove(fname)
            return
        sound = AudioSegment.from_file(fname)
        sound = effects.pan(sound, +1.0)
        await message.edit("Отправляем...")
        m = io.BytesIO()
        if v:
            m.name = "voice.ogg"
            sound.export(m, format="ogg", bitrate="64k", codec="libopus")
            await message.client.send_file(message.to_id, m, reply_to=reply.id, voice_note=True)
        else:
            m.name = "Right.mp3"
            sound.export(m, format="mp3")
            await message.client.send_file(message.to_id, m, reply_to=reply.id, attributes=[
                types.DocumentAttributeAudio(duration=reply.document.attributes[0].duration, title="Right",
                                             performer="Right")])
        await message.delete()

    async def normscmd(self, message):
        v = False
        reply = await message.get_reply_message()
        if not reply:
            await message.edit("А где реплай?")
            return
        await message.edit("Скачиваем...")
        fname = await message.client.download_media(message=reply.media)
        await message.edit("Нормализуем звук...")
        if fname.endswith(".oga") or fname.endswith(".ogg"):
            v = True
            audio = AudioSegment.from_file(fname)
        elif fname.endswith(".mp3") or fname.endswith(".m4a") or fname.endswith(".wav"):
            audio = AudioSegment.from_file(fname)
        else:
            await message.edit("<b>Unsupported format!</b>")
            os.remove(fname)
            return
        sound = AudioSegment.from_file(fname)
        sound = effects.normalize(sound)
        await message.edit("Отправляем...")
        m = io.BytesIO()
        if v:
            m.name = "voice.ogg"
            audio.split_to_mono()
            sound.export(m, format="ogg", bitrate="64k", codec="libopus")
            await message.client.send_file(message.to_id, m, reply_to=reply.id, voice_note=True)
        else:
            m.name = "Normalized.mp3"
            sound.export(m, format="mp3")
            await message.client.send_file(message.to_id, m, reply_to=reply.id, attributes=[
                types.DocumentAttributeAudio(duration=reply.document.attributes[0].duration, title="Left",
                                             performer="Left")])
        await message.delete()

    async def byrobertscmd(self, message):
        v = False
        reply = await message.get_reply_message()
        if not reply:
            await message.edit("А где реплай?")
            return
        await message.edit("Скачиваем...")
        fname = await message.client.download_media(message=reply.media)
        await message.edit("Делаем магию...")
        if fname.endswith(".oga") or fname.endswith(".ogg"):
            v = True
            audio = AudioSegment.from_file(fname)
        elif fname.endswith(".mp3") or fname.endswith(".m4a") or fname.endswith(".wav"):
            audio = AudioSegment.from_file(fname)
        else:
            await message.edit("<b>Unsupported format!</b>")
            os.remove(fname)
            return
        if os.path.isfile("directed.mp3") == False:
            open("directed.mp3", "wb").write(requests.get(
                "https://raw.githubusercontent.com/Daniel3k00/files-for-modules/master/directed.mp3").content)
        audio.export("temp.mp3", format="mp3")
        os.remove(fname)
        out = AudioSegment.empty()
        out += AudioSegment.from_file("temp.mp3")
        out += AudioSegment.from_file("directed.mp3").apply_gain(+10)
        await message.edit("Отправляем...")
        m = io.BytesIO()
        if v:
            m.name = "voice.ogg"
            audio.split_to_mono()
            out.export(m, format="ogg", bitrate="64k", codec="libopus")
            await message.client.send_file(message.to_id, m, reply_to=reply.id, voice_note=True)
        else:
            m.name = "DirectedAudio.mp3"
            out.export(m, format="mp3")
            await message.client.send_file(message.to_id, m, reply_to=reply.id, attributes=[
                types.DocumentAttributeAudio(duration=reply.document.attributes[0].duration, title="Directed",
                                             performer="Robert B. Weide")])
        await message.delete()
        os.remove("temp.mp3")
        os.remove("directed.mp3")

    async def cutcmd(self, event):
        """Используй .cut <начало(сек):конец(сек)> <реплай на аудио/видео/гиф>."""
        args = utils.get_args_raw(event).split(':')
        reply = await event.get_reply_message()
        if not reply or not reply.media:
            return await event.edit('Reply to media')
        if reply.media:
            if args:
                if len(args) == 2:
                    try:
                        await event.edit('Downloading...')
                        smth = reply.file.ext
                        await event.client.download_media(reply.media, f'uncutted{smth}')
                        await event.edit('Cutting...')
                        os.system(f'ffmpeg -i uncutted{smth} -ss {args[0]} -to {args[1]} -c copy cutted{smth} -y')
                        await event.edit('Sending...')
                        await event.client.send_file(event.to_id, f'cutted{smth}', reply_to=reply.id)
                        os.system('rm -rf uncutted* cutted*')
                        await event.delete()
                    except:
                        await event.edit('Reply to media')
                        os.system('rm -rf uncutted* cutted*')
                        return
                else:
                    return await event.edit('No arguments')
            else:
                return await event.edit('No arguments')

    async def fvcmd(self, message):
        reply = await message.get_reply_message()
        lvl = 0
        if not reply:
            await message.edit("Reply to media")
            return
        if utils.get_args_raw(message):
            ar = utils.get_args_raw(message)
            try:
                int(ar)
                if int(ar) >= 10 and int(ar) <= 100:
                    lvl = int(ar)
                else:
                    await message.edit("No Argument")
                    return
            except Exception as exx:
                await message.edit("No Argument" + str(exx))
                return
        else:
            lvl = 100
        await message.edit("<b>Distorting...</b>")
        sa = False
        m = io.BytesIO()
        fname = await message.client.download_media(message=reply.media)
        if (fname.endswith(".oga") or fname.endswith(".ogg")):
            audio = AudioSegment.from_file(fname, "ogg")
        elif fname.endswith(".mp3") or fname.endswith(".m4a") or fname.endswith(".3gp") or fname.endswith(
                ".mpeg") or fname.endswith(".wav"):
            sa = True
            audio = AudioSegment.from_file(fname, "mp3")
        else:
            await message.edit("No file</b>")
            os.remove(fname)
            return
        audio = audio + lvl
        if (sa):
            m.name = "Distorted.mp3"
            audio.export(m, format="mp3")
        else:
            m.name = "voice.ogg"
            audio.split_to_mono()
            audio.export(m, format="ogg", codec="libopus", bitrate="64k")
        m.seek(0)
        if (sa):
            await message.client.send_file(message.to_id, m, reply_to=reply.id, attributes=[
                types.DocumentAttributeAudio(duration=reply.document.attributes[0].duration, title=f"Distorted",
                                             performer="Distort")])
        else:
            await message.client.send_file(message.to_id, m, reply_to=reply.id, voice_note=True)
        await message.delete()
        os.remove(fname)