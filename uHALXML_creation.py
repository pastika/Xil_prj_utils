from .uHALXMLProducerFactory import UHALXMLProducerFactory

from pyfdt.pyfdt import FdtBlobParse
import json
import os

def produceuHALXML(dtboPath, ip_repos:list, base_dir):
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
    print(producerLocations)
    uXMLProd = UHALXMLProducerFactory(producerLocations)

    #Scan over device tree fragment and create uHAL XML file
    for ip in fragment:
        try:
            # Find IP handler and call it if it exists
            uXMLProd[ip](fragment[ip])
        except(KeyError):
            #its ok if an element has no handler
            pass

if __name__ == "__main__":
    produceuHALXML("../tileboard-tester-v1p0/device-tree/pl.dtbo", [], ".")
