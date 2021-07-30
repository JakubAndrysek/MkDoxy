import xmltodict as xd
import pprint

# with open('cpp_basic/doc/xml/class_car.xml','r') as f:
with open('cpp_basic/doc/xml/index.xml','r') as f:
    d = xd.parse(f.read())
    pprint.pprint(d["doxygenindex"])
