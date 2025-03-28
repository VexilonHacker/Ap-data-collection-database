import subprocess
import json
import os

def get_wifi_info():
    try:
        # Execute the nmcli command to get WiFi information
        output = subprocess.check_output(['nmcli', '-t', '-f', 'SSID,BSSID,SIGNAL,CHAN,FREQ,SECURITY,WPA-FLAGS,RSN-FLAGS,RATE,BANDWIDTH,MODE,DEVICE,DBUS-PATH', 'dev', 'wifi']).decode('utf-8')

        # Split the output into lines
        lines = output.split('\n')

        # Initialize an empty dictionary to store WiFi information
        wifi_dict = {}

        # Iterate through each line in the output
        for line in lines:
            if line.strip() != '':
                # Split the line into fields
                fields = line.split(':')

                # Extract individual fields
                ssid = fields[0].replace("\\:", ":")
                bssid = ':'.join(fields[1:7]).replace("\\:", ":")  # Join BSSID fields

                # Check if BSSID already exists in the dictionary
                if bssid in wifi_dict:
                    # If BSSID already exists, remove old entry
                    del wifi_dict[bssid]

                signal = fields[7]
                chan = fields[8]
                freq = fields[9].replace("\\:", ":")
                security = fields[10].replace("\\:", ":")
                wpa_flags = fields[11].replace("\\:", ":")
                rsn_flags = fields[12].replace("\\:", ":")
                rate = fields[13]
                bandwidth = fields[14]
                mode = fields[15]
                device=fields[16]
                dbus_path = fields[17]

                # Lookup MAC info
                mac_info = lookup_mac_info(bssid)

                # Construct WiFi information dictionary
                wifi_info = {
                    "SSID": ssid,
                    "BSSID": bssid,
                    "SIGNAL": signal,
                    "CHAN": chan,
                    "FREQ": freq,
                    "SECURITY": security,
                    "WPA-FLAGS": wpa_flags,
                    "RSN-FLAGS": rsn_flags,
                    "RATE": rate,
                    "BANDWIDTH": bandwidth,
                    "MODE": mode,
                    "DEVICE": device,
                    "DBUS-PATH": dbus_path,
                    "MAC_LOOK_UP": mac_info if mac_info else "N/A",
                    "MAC_NO_CLONE": bssid.replace(":", "").replace(" ", "")  # Add MAC key without colons and spaces
                }

                # Add the WiFi information to the dictionary
                wifi_dict[bssid] = wifi_info

        # Return the dictionary of WiFi information
        return wifi_dict

    except Exception as e:
        # Print error message if an exception occurs
        print("Error:", e)
        return {}

def lookup_mac_info(bssid):
    try:
        # Extract the first three parts (OUI) of the BSSID
        bssid_oui = ':'.join(bssid.split(':')[:3])

        # Read the MAC info database file
        with open('mac-info.csv', 'r') as file:
            for line in file:
                fields = line.strip().split(',')
                if fields[0].startswith(bssid_oui):
                    # Format the MAC lookup value without extra quotes and backslashes
                    mac_lookup = ','.join(fields[1:])
                    return mac_lookup.replace('"', '').replace('\\', '')

    except Exception as e:
        # Print error message if an exception occurs
        print("Error:", e)
        return None
if __name__ == "__main__":
    # Specify the file name for saving WiFi information
    file_name = 'sweet_wifi_info_database_collection.json'

    # Check if the JSON file already exists
    if os.path.exists(file_name):
        # Read existing data from the file
        with open(file_name, 'r') as file:
            existing_data = json.load(file)

        # Convert existing_data to a dictionary if it's a list
        if isinstance(existing_data, list):
            existing_data = {entry['BSSID']: entry for entry in existing_data}
    else:
        existing_data = {}  # If file doesn't exist or is empty, initialize existing_data as an empty dictionary

    # Get WiFi information
    wifi_info = get_wifi_info()

    # Update existing data with new WiFi information
    existing_data.update(wifi_info)

    # Save the updated WiFi information to the file
    with open(file_name, 'w') as file:
        json.dump(list(existing_data.values()), file, indent=4)

    # Print a message indicating successful saving
    print("WiFi information has been saved to: " + file_name)

