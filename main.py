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

# lang_list = GoogleTranslator().get_supported_languages()
tts_list = lang.tts_langs()


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
    if lang_code not in tts_list:
        lang_code = "en"

    if should_translate:
        msg = translate(msg, lang_code)

    tts = gTTS(msg, lang=lang_code)
    tts.save(f'{CSGO_DIR}voice_input.mp3')

    sound = AudioSegment.from_mp3(f'{CSGO_DIR}voice_input.mp3')
    sound.export(f'{CSGO_DIR}voice_input.wav', format="wav")


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
{0} #langs - print available languages to console        ;
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

            message_split = line.split(" : ", 1)
            if len(message_split) < 2:
                continue

            author = message_split[0].strip()
            command = message_split[1].strip().split(" ")[0].strip()
            other_player_chat = " : " in line
            ignore = self in line

            if other_player_chat and not ignore:
                translate_to_console(line.split(
                    " : ")[1], other_lang_code, author)
            elif command:
                msg = line.split(command, 1)[1]

                def get_lang(msg):
                    for lang in tts_list:
                        if lang.lower() == msg.strip().lower():
                            return lang

                def log(msg):
                    print(msg)
                    net.write(f"echo {msg}\n".encode())

                if command == "#tr":
                    translate_to_chat(msg, self_lang_code)
                elif command == "#gtr":
                    translate_to_chat(msg, self_lang_code, True)
                elif command == "#tts":
                    text_to_speech(msg)
                    log("generated tts")
                elif command == "#ttts":
                    text_to_speech(msg, self_lang_code, True)
                    log("generated translated tts")
                elif command == "#lang":
                    self_lang_code = get_lang(msg)
                    log(f"set language to {self_lang_code}")
                elif command == "#olang":
                    other_lang_code = get_lang(msg)
                    log(f"set language to {other_lang_code}")
                elif command == "#langs":
                    log("available languages - ")
                    log(', '.join(tts_list))
except ConnectionRefusedError:
    print(
        f'please start csgo with the following launch option: -netconport {PORT}')
    quit()
