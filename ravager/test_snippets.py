import sys

sys.path.append("../")
from ravager.services.mega import Mega
from ravager import ROOT_DIR
# ~1.8 - 2 MBps upload speed
"""
import sys
import time
print ("Hello")
sys.stdout.flush()
time.sleep(10)
print ("World")child.logfile = sys.stdout

"""
#^((\[API:)([a-zA-z0-9:\s\.\\/]*)(\s[0-9:]*\]))

link_1 = "https://mega.nz/file/KBZBFKTD#zzOMC4Gx0hS7ZOWC4YJJI1oYWsRIekYFZUxSVg21oTc"
link = "https://mega.nz/file/fm4wQQIa#cx08m_cPPHywQAhWO0Oahtbqm9WVlHc0v8ttylMOjUA"
link_3 = "https://mega.nz/file/KBZBFKTD#zzOMC4Gx0hS7ZOWC4YJJI1oYWsRIekYFZUxSVg212e54"
link2 = "https://mega.nz/file/TxUwVAKT#NKeLYl6LiRuQIz0ceyyX1WAAs5A_KPjIxIU1ehB0G5E"
mega = Mega()

#login = mega.login(username="vilewizard69@gmail.com",password="5698741230_Dev")
#print(login)
try:
 logged_in = mega.whoami()
except Exception as e:
    print(e)
#download = mega.download(download_path=ROOT_DIR+"Downloads",download_url=link)
#print(download)


"""
check parallel download again with logged in account
1) Check transfer,if exists check against db and notify user but if not continue
1.1) If orphaned download ,cancel all transfer
2) Add one download only and follow it,if error remove directory(the hashed one) and cancel all transfer
3) Follow download till end
--------------
1)Check login using whoami
2) Export session id in case of login
3) If over quota use experimental proxy support

"""



