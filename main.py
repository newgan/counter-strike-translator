from telnetlib import Telnet
from deep_translator import GoogleTranslator
import time

HOST = "127.0.0.1"
PORT = 4747
lang_code = "en"
net = {}

commands = [
 "#gtr",
 "#tr",
 "#lang"
]

def translate(msg, global_chat=False):
    try:
        new_msg = GoogleTranslator(source='auto', target=lang_code).translate(msg.rstrip())
    except:
        "translation failed"
        return
    
    prefix = "say" if global_chat else "say_team"
    
    time.sleep(1)
    net.write(f'{prefix} "{new_msg}"\n'.encode())  
   
def handle_cmd(cmd, msg):
    if(match == "#tr"):
        translate(msg)
    elif(match == "#gtr"):
        translate(msg, True)
    elif(match == "#lang"):
        lang_code = msg.strip()
                
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
{0} #lang - change language to translate to.             ;
{0}                                                      ;
{0}                                                      ;
{0}                                                      ;
{0}                                                      ;
{0}                                                      ;
{0}                                                      ;
{0} -----------------------------------------------------;""".format("echo").encode())
        
        while True:
            line = net.read_until(b"\n").decode()        
            match = [cmd for cmd in commands if(cmd in line)]
            
            if not match:
                continue
            
            match = match[0]
            
            author = line.split(":", 1)[0]
            msg = line.split(match, 1)[1]
            
            handle_cmd(match, msg)                                               
except ConnectionRefusedError:
    print(f'please start csgo with the following launch option: -netconport {PORT}')
    quit()
