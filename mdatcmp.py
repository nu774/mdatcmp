#!/usr/bin/env python
import sys
import struct

def seek2mdat(fp):
    atom_size, atom_name  = struct.unpack('>L4s', fp.read(8))
    if atom_name != 'ftyp':
        raise Exception('%s: seems not a mp4 file' % fp.name)
    fp.seek(atom_size - 8, 1)

    for head in iter(lambda: fp.read(8), ''):
        atom_size, atom_name  = struct.unpack('>L4s', head)
        if atom_size == 1:
            atom_size = struct.unpack('>Q', fp.read(8))
            body_size = atom_size - 16
        else:
            body_size = atom_size - 8
        if atom_name == 'mdat':
            return body_size
        fp.seek(body_size, 1)
    raise Exception("can't find mdat in " + fp.name)

def compare_mdat(files):
    print 'comparing %s' % ', '.join(f.name for f in files)

    mdat_sizes = map(seek2mdat, files)
    if any(x != mdat_sizes[0] for x in mdat_sizes[1:]):
        print 'mdat size is different:'
        for f, size in zip(files, mdat_sizes):
            print '%10d in %s' % (size, f.name)
        return

    rest = mdat_sizes[0]
    while rest > 0:
        dats = [f.read(min(4096, rest)) for f in files]
        if all(not x for x in dats):
            print 'WARNING: premature EOF'
            break
        if any(x != dats[0] for x in dats[1:]):
            print 'difference found in mdat'
            return
        rest -= len(dats[0])
    print 'no difference found in mdat. size: %d' % mdat_sizes[0]

def main():
    try:
        if len(sys.argv) < 3:
            print >>sys.stderr, 'usage: mdatcmp.py FILE1 FILE2'
        else:
            compare_mdat([open(f, 'rb') for f in sys.argv[1:]])
    except Exception as ex:
        print ex

if __name__ == '__main__':
    main()
