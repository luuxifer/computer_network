import bencodepy

# Read the content of the torrent file
with open("05-star.-wars.-4-k-77.1080p.no-dnr.-35mm.x-264-v-1.0-et-hd_archive.torrent", "rb") as f:
    torrent_data = f.read()

# Decode the torrent data
decoded_data = bencodepy.decode(torrent_data)
print(decoded_data)
