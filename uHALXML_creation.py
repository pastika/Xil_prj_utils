from .uHALXMLProducerFactory import UHALXMLProducerFactory

from pyfdt.pyfdt import FdtBlobParse
import json
import os
import shutil

def produceuHALXML(dtboPath, ip_repos:list, base_dir, xmlDir):
    #open device tree
    try:
        with open(dtboPath, "rb") as infile:
            dtb = FdtBlobParse(infile)
            dt = json.loads(dtb.to_fdt().to_json())

        fragment = dt['fragment@2']['__overlay__']
    except(KeyError):
        print("fragment 2 overlay not found!!")
        exit(-1)
    except(IOError):
        print(f"IOError: {dtboPath} not found")
        exit(-1)

    producerLocations = [("uHALXMLProducers", os.path.join(base_dir, "prj_utils"))]
    for ip_repo in ip_repos:
        split_ip_repo = os.path.join(base_dir, ip_repo).split("/")
        producerLocations.append((split_ip_repo[-1], "/".join(split_ip_repo[:-1]) if len(split_ip_repo) > 1 else "."))
    uXMLFact = UHALXMLProducerFactory(producerLocations, fragment)

    #Scan over device tree fragment and create uHAL XML file
    if not os.path.exists(xmlDir):
        os.makedirs(xmlDir)

    with open(os.path.join(xmlDir, "fw_block_addresses.xml"), "w") as f:
        f.write('<?xml version="1.0" encoding="ISO-8859-1"?>\n<node id="TOP">\n')
        for ip in fragment:
            try:
                # Find IP handler and call it if it exists
                producer = uXMLFact[ip]
            except(KeyError) as e:
                #its ok if an element has no handler
                continue
            topNode = producer(fragment[ip], xmlDir)
            f.write("  %s\n"%topNode)

        f.write("</node>\n")

    shutil.copyfile(os.path.join(base_dir, 'prj_utils', 'uHALXMLProducers', 'connections.xml'), os.path.join(xmlDir, 'connections.xml'))

if __name__ == "__main__":
    produceuHALXML("../tileboard-tester-v1p0/device-tree/pl.dtbo", [], ".")
