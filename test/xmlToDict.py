import xmltodict as xd
from pprint import *

# with open('cpp_basic/doc/xml/class_car.xml','r') as f:
with open('cpp_basic/doc/xml/index.xml','r') as f:
    d = xd.parse(f.read())
    pprint(d["doxygenindex"])
    print("________________________________________________________________")
    for par in d["doxygenindex"]["compound"]:
        if "member" in par:
            pprint(par["member"])
        for p in par["@refid"]:
            pprint(p)
