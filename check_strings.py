def hex2dec(s):
    if not s:  # int() will not work on empty strings
        return None, False
    try:
        i = int(s, 16)
        return i, True
    except ValueError:
        return None, False


def is_hex(s):
    _, f = hex2dec(s)
    return f


def is_address_valid(address):
    # checks if: ...
    # ... address is a valid hexadecimal number folowed by H and ...
    # ... addresses always crescent
    if not hasattr(is_address_valid, "prev_address_dec"):
        is_address_valid.prev_address = "-1H"

    address_dec, f_hex_adddress = hex2dec(address[:-1])
    prev_address_dec, f_hex_prev_adddress = hex2dec(is_address_valid.prev_address[:-1])

    is_address_valid.address_dec = address_dec
    is_address_valid.prev_address_dec = prev_address_dec
    is_address_valid.prev_address = address
    return f_hex_adddress and f_hex_prev_adddress and (0 <= address_dec <= 65535 and address_dec > prev_address_dec)


def is_quoted_string(s):
    return s[0] == '"' and s[-1] == '"'


def is_quoted_string_with_cr(s):
    return s.replace(" ", "")[-5:] == '"+0DH'