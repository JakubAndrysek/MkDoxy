# import xmltodict as xd
# from pprint import *
#
# # with open('cpp_basic/doc/xml/class_car.xml','r') as f:
# with open('cpp_basic/doc/xml/index.xml','r') as f:
#     d = xd.parse(f.read())
#     pprint(d["doxygenindex"])
#     print("________________________________________________________________")
#     for par in d["doxygenindex"]["compound"]:
#         if "member" in par:
#             pprint(par["member"])
#         for p in par["@refid"]:
#             pprint(p)

from ssxtd import parsers
from pprint import *

# with open('cpp_basic/doc/xml/class_car.xml','r') as f:
# with open('cpp_basic/doc/xml/index.xml','r') as f:
data = parsers.xml_parse('cpp_basic/doc/xml/main_8cpp.xml', depth=0)

pri = next(data)

pp(pri)
print("")


# from fdp import FileParser
#
# p = FileParser("cpp_basic/doc/xml/class_car.xml")
# parsed_dict = p.parse("cpp_basic/doc/xml/class_car.xml")
#
# pp(parsed_dict)

# from bs4 import BeautifulSoup
#
# tei_doc = 'cpp_basic/doc/xml/main.xml'
# with open(tei_doc, 'r') as tei:
#     soup = BeautifulSoup(tei, 'lxml')
#
# pp(soup.detaileddescription.para.parameterlist.getText())