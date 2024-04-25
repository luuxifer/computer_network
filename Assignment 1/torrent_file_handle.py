import bencodepy
import hashlib
from collections import OrderedDict
from beautifultable import BeautifulTable

class metadata_file():
    def __init__(self, announce_list, piece_length, pieces, file_name, file_length, info_hash, files):
        self.announce_list = announce_list
        self.piece_length = piece_length
        self.pieces = pieces
        self.file_name = file_name
        self.file_length = file_length
        self.info_hash = info_hash
        self.files = files

class metadata_reader():
    def __init__(self, torrent_file_path) -> None:
        try:
            self.torrent_file_raw_extract = bencodepy.decode_from_file(torrent_file_path)
        except Exception as err: 
            pass

        # check if encoding scheme is given in dictionary
        if b'encoding' in self.torrent_file_raw_extract.keys():
            self.encoding = self.torrent_file_raw_extract[b'encoding'].decode()
        else:
            self.encoding = 'UTF-8'

        self.torrent_file_extract = self.extract_metadata_file(self.torrent_file_raw_extract)
        
        # check if there is more than one tracker
        if 'announce-list' in self.torrent_file_extract.keys():
            announce_list = self.torrent_file_extract['announce_list']
        else:
            announce_list = self.extract_metadata_file['announce']

        file_name = self.torrent_file_extract['info']['name']
        piece_length = self.torrent_file_extract['info']['piece length']
        pieces = self.torrent_file_extract['info']['pieces']

        info_hash = self.generate_info_hash()

        files = None

        # Check if the torrent file contains multiple file paths
        if 'files' in self.torrent_file_extract['info'].keys():
            # info_file : [length, path]
            file_list = self.torrent_file_extract['info']['files']
            files = [(file_data['length'], file_data['path']) for file_data in file_list]
            file_length = 0
            for length, _ in files:
                file_length += length
        else:
            file_length = self.torrent_file_extract['info']['length']

        # Constructor
        super().__init__(announce_list, piece_length, pieces, file_name, file_length, info_hash, files)

    def extract_metadata_file(self, torrent_file_raw_extract: dict):
        torrent_file_content = OrderedDict()

        for key, val in torrent_file_raw_extract.items():
            key = key.decode(self.encoding)
            if isinstance(val, dict):
                val = self.extract_metadata_file(val)
            torrent_file_content[key] = val

        return torrent_file_content
    
    def generate_info_hash(self):
        sha1_hash = hashlib.sha1()
        raw_info = self.torrent_file_raw_extract[b'info']
        sha1_hash.update(bencodepy.encode(raw_info))
        return sha1_hash.digest()
    
    def get_data(self):
        return metadata_file(self.announce_list, self.piece_length, self.pieces, self.file_name, self.file_length, self.info_hash, self.file_path)

    # provides torrent file full information
    def __str__(self):
        torrent_file_table = BeautifulTable()
        torrent_file_table.columns.header = ["TORRENT FILE DATA", "DATA VALUE"]
        
        tracker_urls = self.trackers_url_list[0]
        if len(self.trackers_url_list) < 3:
            for tracker_url in self.trackers_url_list[1:]:
                tracker_urls += '\n' + tracker_url 
        else:
            tracker_urls += '\n... ' 
            tracker_urls += str(len(self.trackers_url_list)-1) + ' more tracker urls !' 
        
        # tracker urls
        torrent_file_table.rows.append(['Tracker List', tracker_urls])
        # file name
        torrent_file_table.rows.append(['File name', str(self.file_name)])
        # file size
        torrent_file_table.rows.append(['File size', str(self.file_size) + ' B'])
        # piece length 
        torrent_file_table.rows.append(['Piece length', str(self.piece_length) + ' B'])
        # info hash 
        torrent_file_table.rows.append(['Info Hash', '20 Bytes file info hash value'])
        # files (multiple file torrents)
        if self.files:
            torrent_file_table.rows.append(['Files', str(len(self.files))])
        else:
            torrent_file_table.rows.append(['Files', str(self.files)])
        
        return str(torrent_file_table)
