from torrentool.api import Torrent as tor


class Torrent:
    def __init__(self):
        pass

    @staticmethod
    def to_magnet(torrent_path):
        torrent = tor.from_file(str(torrent_path))
        announce_str = []
        for i in torrent.announce_urls:
            for j in i:
                announce_str.append({"tr": str(j)})
        st = "tr=" + "&tr=".join(i["tr"] for i in announce_str)
        magnet_string = "{}&dn={}&".format(torrent.magnet_link, torrent.name)
        magnet_string = magnet_string + st
        return str(magnet_string)
