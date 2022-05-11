import json
import re
from datetime import datetime

"""
The following is a sample JSON object containing data on transcoder with MAC Address 14:91:82:3C:D6:7D with info on
processed octets.
"""
aristaTranscoder = """
    [{
        "Device": "Arista",
        "Model": "X-Video",
        "NIC": [
            {
                "Description": "Linksys ABR",
                "MAC": "14:91:82:3C:D6:7D",
                "Timestamp": "2020-03-23T18:25:43.511Z",
                "Rx": "3698574500",
                "Tx": "122558800"
            }
        ]
    },

    {
        "Device": "Arista",
        "Model": "X-Video",
        "NIC": [
            {
                "Description": "Linksys ABR",
                "MAC": "14:91:82:3C:D6:7D",
                "Timestamp": "2020-03-23T18:25:45.512Z",
                "Rx": "3699595135",
                "Tx": "123658800"
            }
        ]
    }]
"""

"""
This function parses the timestamp string and returns it as a formatted timestamp using datetime module. This allows me 
to compare timestamps and obtain time difference.    
"""


def getTimeStamp(timestamp):
    format_date = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%f%z')
    return format_date
    # timestampPattern = '\d{2}:\d{2}:\d{2}.\d{3}'
    # res = re.search(timestampPattern, timestamp)
    # return res.group(0)


"""
This function parses the JSON data and organizes it into a python dictionary. Network Interface controllers are 
organized and grouped by MAC address.
"""


def parseJSON(transcoder_json):
    network_interfaces = {"device": "Arista", "model": "X-Video", "nic": {}}
    data = json.loads(transcoder_json)

    for driver in data:
        if str(driver["NIC"][0]["MAC"]) in network_interfaces["nic"].keys():
            macAddr = str(driver["NIC"][0]["MAC"])
            network_interfaces["nic"][macAddr].append({
                "description": driver["NIC"][0]["Description"],
                "timestamp": driver["NIC"][0]["Timestamp"],
                "Rx": int(driver["NIC"][0]["Rx"]),
                "receivRate": 0,
                "Tx": int(driver["NIC"][0]["Tx"]),
                "transmitRate": 0
            })
        else:
            network_interfaces["nic"].update({str(driver["NIC"][0]["MAC"]): [{
                "description": driver["NIC"][0]["Description"],
                "timestamp": driver["NIC"][0]["Timestamp"],
                "Rx": int(driver["NIC"][0]["Rx"]),
                "receiveRate": 0,
                "Tx": int(driver["NIC"][0]["Tx"]),
                "transmitRate": 0
            }]})

    return network_interfaces
    # transcoder = xVideo(driver["Device"], driver["Model"], driver["NIC"])
    # transcoder.printInfo()
    # network_interfaces.append(transcoder)


"""
This function goes through the content in the dictionary and calculates all the bit rate for Rx and Tx of each 
Network Interface Controller. Bitrate is calculated in Mbps.
"""


def getBitRates(transcoder_dict):
    for driver in transcoder_dict["nic"]:
        for i in transcoder_dict["nic"][driver]:
            if transcoder_dict["nic"][driver].index(i) == 0:
                rx = transcoder_dict["nic"][driver][0]["Rx"]
                tx = transcoder_dict["nic"][driver][0]["Tx"]
                transcoder_dict["nic"][driver][0]["receiveRate"] = ((rx * 8) * 2) / 10000000
                transcoder_dict["nic"][driver][0]["transmitRate"] = ((tx * 8) * 2) / 10000000
            else:
                """
                Difference between time and bits processed of current and previous moment is obtained and then used to 
                calculate bitrate.
                """
                transIdx = transcoder_dict["nic"][driver].index(i)
                rx = transcoder_dict["nic"][driver][transIdx]["Rx"]
                tx = transcoder_dict["nic"][driver][transIdx]["Tx"]
                prevRx = transcoder_dict["nic"][driver][transIdx - 1]["Rx"]
                prevTx = transcoder_dict["nic"][driver][transIdx - 1]["Tx"]
                rxDiff = rx - prevRx
                txDiff = tx - prevTx
                currentTime = getTimeStamp(transcoder_dict["nic"][driver][transIdx]["timestamp"])
                prevTime = getTimeStamp(transcoder_dict["nic"][driver][transIdx - 1]["timestamp"])
                difference = currentTime - prevTime
                timeDiff = difference.seconds

                transcoder_dict["nic"][driver][transIdx]["receiveRate"] = ((rxDiff * 8) * 2) / 10000000
                transcoder_dict["nic"][driver][transIdx]["transmitRate"] = ((txDiff * 8) * 2) / 10000000


if __name__ == "__main__":
    dict = parseJSON(aristaTranscoder)
    getBitRates(dict)

    for item in dict:
        if item == "nic":
            print("NIC: ")
            for mac in dict[item]:
                print("MAC: %s" % mac)
                for moment in dict[item][mac]:
                    momentIdx = dict[item][mac].index(moment)
                    print(dict[item][mac][momentIdx])
        else:
            print(dict[item])
