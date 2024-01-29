# noinspection PyUnresolvedReferences
from typing import Union, Optional
import xml.etree.ElementTree as et
def dumps(data):
    """
    Convert a simple dict of key/value pairs into XML
    """
    elem = et.Element("root")
    for key, val in data.items():
        child = et.SubElement(elem, key)
        child.text = str(val)
    return et.tostring(elem)

def dict_to_tree(data: dict, parent: Optional[et.Element]=None):
    if parent is None:
        parent = et.Element("root")
    for key, value in data.items():
        if isinstance(value, (str, int, float)):
            el = et.SubElement(parent, key)
        # elif isinstance()





