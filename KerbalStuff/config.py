import logging

try:
    from configparser import ConfigParser
except ImportError:
    # Python 2 support
    from ConfigParser import ConfigParser

logger = logging.getLogger("KerbalStuff")
logger.setLevel(logging.DEBUG)

sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
sh.setFormatter(formatter)

logger.addHandler(sh)

# scss logger
logging.getLogger("scss").addHandler(sh)

config = ConfigParser()
config.readfp(open('config.ini'))
env = 'dev'

_cfg = lambda k: config.get(env, k)
_cfgi = lambda k: int(_cfg(k))

class MailBans:
    bans = list()
    def __init__(self):
        with open('mailbans.txt') as f:
            self.bans = f.readlines()
            for i, mail in enumerate(self.bans):
                self.bans[i] = mail.replace('\n', '')
            print(self.bans)
                
    def isMailBanned(self, mail):
        splitMail = mail.split('@')
        print(splitMail)
        if len(splitMail)<2:
            return False
        elif splitMail[1].strip() in self.bans:
                return True
        else:
            return False
        
_mailbans = MailBans()