"""Rename SFNT font identity records while preserving copyright and glyph data."""
import struct


def checksum(value):
    value += bytes((-len(value)) % 4)
    return sum(struct.unpack(f'>{len(value) // 4}I', value)) & 0xffffffff


def port_font(original):
    data = bytearray(original)
    tables = {}
    for index in range(struct.unpack_from('>H', data, 4)[0]):
        position = 12 + 16 * index
        tag, _, offset, length = struct.unpack_from('>4sIII', data, position)
        tables[tag] = (position, offset, length)
    _, offset, _ = tables[b'name']
    _, count, storage = struct.unpack_from('>HHH', original, offset)
    identities = {1, 2, 3, 4, 6, 16, 17}
    for index in range(count):
        record = offset + 6 + 12 * index
        platform, _, _, identity, length, relative = struct.unpack_from('>6H', original, record)
        if identity not in identities:
            continue
        start = offset + storage + relative
        encoding = 'utf-16-be' if platform in (0, 3) else 'mac_roman'
        text = original[start:start + length].decode(encoding)
        renamed = text.replace('OMARCHY', 'GRAN').replace('Omarchy', 'Gran').replace('omarchy', 'gran')
        payload = renamed.encode(encoding)
        if len(payload) > length:
            raise ValueError('New font identity does not fit the name record')
        data[start:start + len(payload)] = payload
        struct.pack_into('>H', data, record + 8, len(payload))
    _, head, _ = tables[b'head']
    struct.pack_into('>I', data, head + 8, 0)
    for _, (record, start, length) in tables.items():
        struct.pack_into('>I', data, record + 4, checksum(bytes(data[start:start + length])))
    struct.pack_into('>I', data, head + 8, (0xB1B0AFBA - checksum(bytes(data))) & 0xffffffff)
    return bytes(data)
