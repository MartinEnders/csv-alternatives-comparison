#!/usr/bin/python3

import csv
import json
import bson # pip3 install bson
from xml.etree import ElementTree as ET
from xml.dom import minidom
import glob
import os
import gzip
import shutil

# Function for gzipping files
def gzip_file(file_name):
    with open(file_name, 'rb') as f_in:
        with gzip.open(file_name + '.gz', 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)


# comparison of size from different output formats 

# list of lists
data = []

# Reading values from a list of german words
# The wordfile I used can be downloaded at https://sourceforge.net/projects/germandict/
print("Generate data structure")
with open('german.dic','r',encoding='latin-1',newline='\r\n') as dict_in:
    for n in range(256000): # lines 
        line = []
        for j in range(7): # values
            line.append(dict_in.readline().rstrip())
        data.append(line)

# write csv
print("write csv")
with open("output.csv", "w",encoding='utf-8') as f:
    writer = csv.writer(f,quoting=csv.QUOTE_MINIMAL)
    writer.writerows(data)

# write json
print("write json")
with open("output.json", "w", encoding='utf-8') as f:
    json_object = {"header" : data[0],
                   "data" : data[1:]}
    json.dump(json_object,f)

# write pretty-json with indent
print("write pretty-json")
with open("output.pretty-json", "w", encoding='utf-8') as f:
    json_object = {"header" : data[0],
                   "data" : data[1:]}
    json.dump(json_object,f, indent=4)
    

# write bson
print("write bson")
with open("output.bson", "wb") as f:
    bson_object = {"header" : data[0],
                   "data" : data[1:]}
    f.write(bson.dumps(bson_object))

# write xml
print("write xml")
with open("output.xml","wb") as f:
    root = ET.Element("export")
    header = ET.SubElement(root,"header")
    body   = ET.SubElement(root,"data")
    for v in data[0]:
        xml_value = ET.SubElement(header,"v")
        xml_value.text = v
    
    for line in data[1:]:
        xml_line = ET.SubElement(body,"l")
        for value in line:
            xml_value = ET.SubElement(xml_line,"v")
            xml_value.text = value
    doc = ET.ElementTree(element=root)
    doc.write(f, encoding="utf-8", xml_declaration=True)

# write pretty-xml with indent
print("write pretty-xml")
with open("output.pretty-xml","wb") as f:
    root = ET.Element("export")
    header = ET.SubElement(root,"header")
    body   = ET.SubElement(root,"data")
    for v in data[0]:
        xml_value = ET.SubElement(header,"v")
        xml_value.text = v
    
    for line in data[1:]:
        xml_line = ET.SubElement(body,"l")
        for value in line:
            xml_value = ET.SubElement(xml_line,"v")
            xml_value.text = value
    doc = ET.ElementTree(element=root)
    
    rough_string = ET.tostring(root, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    f.write(reparsed.toprettyxml(indent="\t", encoding='utf-8'))


# remove .gz from the last run
print("delete .gz files from the last run")
for f in  glob.glob("output.*.gz"):
    os.remove(f)    

# collect created files
file_list = glob.glob("output.*")
print("gzipping files")
for f in file_list:
    print("  gzip " + str(f))
    gzip_file(f)

# csv reference size
plain_csv_file_size = os.path.getsize("output.csv")
gzip_csv_file_size =  os.path.getsize("output.csv.gz")

# print comparisons of output files
for f in file_list:
    print(f + "[gz]")
    plain_size = os.path.getsize(f)
    gzip_size = os.path.getsize(f+".gz")
    ratio = round(gzip_size / plain_size * 100, 2)
    print("Size in bytes: {} [gz: {}], Ratio: plain/gzip: {}".format(plain_size, gzip_size, ratio))

    print("  Ratio {}/csv: {}".format(f, round(plain_size/plain_csv_file_size*100,2)))
    print("  Ratio {}.gz/csv.gz: {}".format(f, round(gzip_size/gzip_csv_file_size*100,2)))

