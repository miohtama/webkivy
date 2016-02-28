
from collections import OrderedDict

# https://www.eftlab.co.uk/index.php/site-map/knowledge-base/145-emv-nfc-tags
KNOWN_FIELDS = {
    0x50: ("Application label", str),
    0x84: ("Dedicated file", str),
    0xA5: ("FCI Propietary tempalte", dict),
    0x5f2d: ("Language preference", str),
}



def decode_emv(msg, pointer):
    results = OrderedDict()
    pointer = 2
    while pointer < len(msg):

        field_type = ord(msg[pointer])
        field_len = ord(msg[pointer+1])

        print(hex(field_type), field_len)

        known_field_name, known_field_type = KNOWN_FIELDS.get(field_type, (None, None))
        if known_field_type == dict:
            results[known_field_name] = decode_emv(msg, pointer+2)
        elif known_field_type == str:
            results[known_field_name] = msg[pointer+2:pointer+2+field_len]

        pointer += 2 + field_len

if __name__ == "__main__":

    # 6f file control template


    msg = "6f4a8408a000000003101002a53e500a566973612044656269745f2d0266699f38189f66049f02069f03069f1a0295055f2a029a039c019f3704bf0c0f9f5a053109780246bf6304df200180"
    msg = msg.decode("hex")

    results = decode_emv(msg, 2)