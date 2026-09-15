MOBILE_ONLY_OUIS = {
    "00:cd:fe", "f4:0f:24", "bc:d1:d3", # Apple (iPhones/Watch)
    "50:01:d9", "cc:6e:a4", "ec:1f:72", # Samsung Mobile
    "d8:ce:3a", "e8:b4:c8", # Google Pixel
}

def is_mobile_hotspot(bssid: str) -> bool:
    """
    Returns True if the BSSID is identified as a mobile hotspot. It combines checking the LAA (Locally Administered Address) bit and filtering by the OUI of mobile devices.
    """
    if not bssid:
        return True

    clean_bssid = bssid.replace(":", "").replace("-", "").strip().lower()


    # Malformed BSSIDs
    if len(clean_bssid) < 12:
        return True

    # Bit LAA (Locally Administered Bit)
    second_char = clean_bssid[1]
    if second_char in {'2', '3', '6', '7', 'a', 'b', 'e', 'f'}:
        return True

    # OUI filtering
    formatted_oui = f"{clean_bssid[0:2]}:{clean_bssid[2:4]}:{clean_bssid[4:6]}"
    if formatted_oui in MOBILE_ONLY_OUIS:
        return True

    return False