from telnetlib import Telnet
from deep_translator import GoogleTranslator
import time
from gtts import gTTS
from gtts import lang
from pydub import AudioSegment

HOST = "127.0.0.1"
PORT = 4747
net = {}

CSGO_DIR = "C:/Program Files (x86)/Steam/steamapps/common/Counter-Strike Global Offensive/"

commands = [
    "#gtr",
    "#tr",
    "#lang",
    "#olang",
    "#tts",
    "#ttts",
]

lang_list = GoogleTranslator().get_supported_languages()
voice_list = lang.tts_langs()


def translate(msg, lang_code):
    try:
        return GoogleTranslator(
            source='auto', target=lang_code).translate(msg.rstrip())
    except:
        "translation failed"
        return


def translate_to_chat(msg, lang_code, global_chat=False):
    new_msg = translate(msg, lang_code)

    if not new_msg:
        return

    prefix = "say" if global_chat else "say_team"

    time.sleep(1)
    net.write(f'{prefix} "{new_msg}"\n'.encode())


def translate_to_console(msg, lang_code, author):
    new_msg = translate(msg, lang_code)

    if new_msg and new_msg in msg:  # language is the same
        return

    net.write(f'echo {author}(TRANSLATED): "{new_msg}"\n'.encode())


def text_to_speech(msg, lang_code="en", should_translate=False):
    if lang_code not in voice_list:
        lang_code = "en"

    if should_translate:
        msg = translate(msg, lang_code)

    tts = gTTS(msg, lang=lang_code)
    tts.save(f'{CSGO_DIR}voice_input.mp3')

    sound = AudioSegment.from_mp3(f'{CSGO_DIR}voice_input.mp3')
    sound.export(f'{CSGO_DIR}voice_input.wav', format="wav")

    print("generated tts")


def get_self_name():
    net.write("name\n".encode())

    while True:
        line = net.read_until(b"\n").decode()
        if ('"name"' in line):
            return line.split('" ( def')[0].split('name" = "')[1]


try:
    with Telnet(host=HOST, port=PORT) as net:
        print("connected to console!")

        net.write("clear\n".encode())
        net.write("""
{0} -----------------------------------------------------;
{0} ------------- welcome to cs translator! -------------;
{0} -----------------------------------------------------;
{0} #gtr - send a translated message to global chat.     ;
{0} #tr - send a translated message to team chat.        ;
{0} #tts - TTS a message in your default language.       ;
{0} #ttts - TTS a translated message.                    ;
{0} #lang - change language to translate to (self).      ;
{0} #olang - change language to translate to (other).    ;
{0}                                                      ;
{0}                                                      ;
{0}                                                      ;
{0} -----------------------------------------------------;\n""".format("echo").encode())

        # workaround to ignore the header message
        time.sleep(3)
        net.read_very_eager()

        self = get_self_name()

        self_lang_code = "en"
        other_lang_code = "en"

        net.write("voice_inputfromfile 1\n".encode())

        while True:
            try:
                line = net.read_until(b"\n").decode()
            except:
                continue

            match = next((cmd for cmd in commands if (cmd in line)), None)
            author = line.split(":", 1)[0]

            other_player_chat = " : " in line
            ignore = self in line

            if other_player_chat and not ignore:
                translate_to_console(line.split(
                    " : ")[1], other_lang_code, author)
            elif match:
                msg = line.split(match, 1)[1]

                if match == "#tr":
                    translate_to_chat(msg, self_lang_code)
                elif match == "#gtr":
                    translate_to_chat(msg, self_lang_code, True)
                elif match == "#tts":
                    text_to_speech(msg)
                elif match == "#ttts":
                    text_to_speech(msg, self_lang_code, True)
                elif match == "#lang":
                    for lang in voice_list:
                        if lang.lower() == msg.strip().lower():
                            self_lang_code = lang
                elif match == "#olang":
                    for lang in voice_list:
                        if lang.lower() == msg.strip().lower():
                            other_lang_code = lang
except ConnectionRefusedError:
    print(
        f'please start csgo with the following launch option: -netconport {PORT}')
    quit()
