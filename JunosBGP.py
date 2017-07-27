#!/usr/bin/env python3

from pprint import pprint
import requests
import jinja2
import json
import yaml
from jnpr.junos import Device
from jnpr.junos.utils.config import Config

                                                                # BGP configuration template for IPv4 and IPv6 below.
template = '''                                                     
  protocols {
    BGP {
  {%- for lan in lans -%}  
    GROUP PEERSv4 {
     NEIGHBOURS {{lan.ipaddr4}} {
        DESCRIPTION {{net.name}};
        LOCAL-DETAILS {{lan.name}} {{lan.asn}}-{{lan.ix_id}};
        PEER-AS {{lan.asn}};
                            }
                }
    GROUP PEERSv6 {
     NEIGHBOURS {{lan.ipaddr6}} {
        DESCRIPTION {{net.name}};
        LOCAL-DETAILS {{lan.name}} {{lan.asn}}-{{lan.ix_id}};
        PEER-AS {{lan.asn}};
                            }
                }    
  {% endfor -%}  
        }
            }                         
'''

def pdb_query(asn):

    r = requests.get("https://www.peeringdb.com/api/net?asn={}&depth=2".format(asn))
    return r.json()['data'][0]

def tmpl(data):

    t = jinja2.Template(template)                               # Declare a template with jinja2 library/module

    a = 0
    Lans=[]

    while a < len(data['netixlan_set']):
        if data['netixlan_set'][a]['ix_id'] == 13:              # Parsing only for SIX-Seattle with IX ID of 13
            Lans.append(data['netixlan_set'][a])
            a = a+1
        else:
            a = a+1

    out = t.render(net=data, lans=Lans)                         # Render values to the template
    return out

def JunosConn(configs):

    mxs = {                                                     # Declaring Juniper device details
        'host': '192.168.10.1',
        'user': 'fortune',
        'password': 'blues',
    }

    dev = Device(**mxs)
    dev.open()

    print()
    print(yaml.dump(dev.facts))                     # Printing device facts such as model, serial number, version etc...
    print("Facts in json format:")
    print(json.dumps(dev.facts))

    cfg = Config(dev)
    cfg.load(configs, format="text", merge=True)               # Pushing configurations over the device
    cfg.pdiff()
    cfg.commit()

def main():

    data = pdb_query(20115)                                    # function call to get IX details in json format

    result = tmpl(data)                                        # function call to get final configurations
    pprint(result)

    JunosConn(result)                                          # function call to connect and push configs over Juniper

if __name__ == "__main__":

    main()




