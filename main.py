from telnetlib import Telnet
from deep_translator import GoogleTranslator

HOST = "127.0.0.1"
PORT = 4747
lang_code = "en"
net = {}
commands = ["#gtr", "#tr", "#lang"]

def translate(msg, global_chat=False):
    new_msg = GoogleTranslator(source='auto', target=lang_code).translate(msg.rstrip())
    
    prefix = "say" if global_chat else "say_team"
    net.write(f'{prefix} "{new_msg}"\n'.encode())  
try:
    with Telnet(host=HOST, port=PORT) as net:
        print("connected!")
        
        while True:
            line = net.read_until(b"\n").decode()        
            match = [cmd for cmd in commands if(cmd in line)]
            
            if not match:
                continue
            
            match = match[0]
            
            author = line.split(":", 1)[0]
            msg = line.split(match, 1)[1]
            
            if(match == "#tr"):
                translate(msg)
            elif(match == "#gtr"):
                translate(msg, True)
            elif(match == "#lang"):
                lang_code = msg.strip()
                                           
except ConnectionRefusedError:
    print(f'please start csgo with the following launch option: -netconport {PORT}')
