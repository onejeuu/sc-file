import struct
from bencodepy import encode
from typing import List, Dict, Any
import sys

def read_utf(data: bytes, offset: int) -> tuple[str, int]:
    length = struct.unpack_from('>H', data, offset)[0]
    string = data[offset + 2:offset + 2 + length].decode('utf-8')
    return string, offset + 2 + length

def read_torrent_file(data: bytes, offset: int) -> tuple[Dict[str, Any], int]:
    path, offset = read_utf(data, offset)
    size = struct.unpack_from('>Q', data, offset)[0]
    offset += 8
    hash_bytes = data[offset:offset + 20]
    offset += 20
    return {'path': path, 'length': size, 'hash': hash_bytes}, offset

def read_stalcraft_torrent(filename: str) -> Dict[str, Any]:
    with open(filename, 'rb') as f:
        data = f.read()

    offset = 0
    // skip signature (8 bytes)
    offset += 8
    // read comment (UTF)
    comment, offset = read_utf(data, offset)
    // read tracker count (4 bytes)
    tracker_count = struct.unpack_from('>I', data, offset)[0]
    offset += 4
    // read trackers (array of UTF strings)
    trackers = []
    for _ in range(tracker_count):
        tracker, offset = read_utf(data, offset)
        trackers.append(tracker)
    // read reserved string (UTF, empty)
    _, offset = read_utf(data, offset)
    // Read piece length (4 bytes)
    piece_length = struct.unpack_from('>I', data, offset)[0]
    offset += 4
    // read torrent name (UTF)
    name, offset = read_utf(data, offset)
    // read file count (4 bytes)
    file_count = struct.unpack_from('>I', data, offset)[0]
    offset += 4
    // read files
    files = []
    for _ in range(file_count):
        file_info, offset = read_torrent_file(data, offset)
        files.append(file_info)
    // read hash count (4 bytes)
    hash_count = struct.unpack_from('>I', data, offset)[0]
    offset += 4
    // read piece hashes
    pieces = data[offset:offset + hash_count * 20]
    if len(pieces) != hash_count * 20:
        raise ValueError(f"Expected {hash_count * 20} bytes for pieces, got {len(pieces)}")

    // Construct Bencode-compatible dictionary
    torrent_dict = {
        'encoding': 'UTF-8',
        'publisher': 'EXBO',
        'comment': comment,
        'announce': trackers[0] if trackers else '',
        'announce-list': [[tracker] for tracker in trackers],
        'created by': 'Art3mLapa',
        'publisher-url': 'https://stalcraft.ru',
        'info': {
            'name': name,
            'piece length': piece_length,
            'pieces': pieces,
            'files': [
                {
                    'length': file['length'],
                    'path': file['path'].split('/'),
                    'true_path': file['path'].split('/')
                } for file in files
            ]
        }
    }
    return torrent_dict

def convert_to_torrent(input_file: str, output_file: str):
    torrent_dict = read_stalcraft_torrent(input_file)
    with open(output_file, 'wb') as f:
        f.write(encode(torrent_dict))

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python convert_stalcraft_torrent.py stalcraft.torrent.bin output.torrent")
        sys.exit(1)
    convert_to_torrent(sys.argv[1], sys.argv[2])
    print(f"Converted {sys.argv[1]} to {sys.argv[2]}")
