#!/usr/bin/python
import xml.etree.ElementTree
import re

def updateVersion(old_v):
    (major, minor, patch) = map(lambda x: int(x, 10),
                                re.findall('(\d+)\.(\d+)\.(\d+)', old_v)[0])
    patch += 1
    return '%d.%d.%d' % (major, minor, patch)

def main():
    tree = xml.etree.ElementTree.parse('addon.xml')
    old_v = tree.getroot().get('version')
    new_v = updateVersion(old_v)
    tree.getroot().set('version', new_v)
    tree.write('addon.xml')
    print new_v

if __name__ == "__main__":
    main()
