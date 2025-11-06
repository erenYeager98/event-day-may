import base64
encoded = "dSIifSFHPDxvI3RvfCN7Iic7ciByeydybnRyIDpxeDt5diRyPCJyIHp2e255"

decoded_bytes = base64.b64decode(encoded)
rot_text = decoded_bytes.decode('utf-8')

def rot_n(s, n=13):
    out = []
    for ch in s:
        if 32 <= ord(ch) <= 126:
            out.append(chr((ord(ch) - 32 - n) % 95 + 32)) 
        else:
            out.append(ch)
    return ''.join(out)

flag = rot_n(rot_text, 13)
print("FLAG:", flag)
