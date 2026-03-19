from fix_constants import * 


def fix_address(address, hash, type="code"):
    # this is not one of the expected files: do nothing
    if hash not in FIX_LIST:
        return None, address

    fix_elements = FIX_LIST[hash]

    # initialize the attributes on the first time
    if type not in fix_address.count_addresseses:
        fix_address.count_addresseses[type] = {}

    if type not in fix_address.address_stop_skipping:
        fix_address.address_stop_skipping[type] = {}
        
    # even if it os not an address of interest the function can still be on SKIP state
    if fix_address.address_stop_skipping[type] != {}:
        if fix_address.address_stop_skipping[type] == address:
            # skiping part ended return to normal
            fix_address.address_stop_skipping[type] = {}
            return None, address
        else:
            # it is on SKIP state: skip
            return SKIP, address

    if address not in fix_elements:
        return None, address

    # can only reach this point if it is an address of interest

    # count ocurrencies of the address
    if address not in fix_address.count_addresseses[type]:
        fix_address.count_addresseses[type][address] = 1
    else:
        fix_address.count_addresseses[type][address] += 1

    count, action, new_address = fix_elements[address]
    if count == fix_address.count_addresseses[type][address]:
        # the address has the necessary count
        # TODO here we can use a switch
        if action == SKIP:
            fix_address.address_stop_skipping[type] = new_address
            return SKIP, None
        elif action == SUBSTITUTE:
            return SUBSTITUTE, new_address
        elif action == INSERT_NEXT:
            return INSERT_NEXT, new_address
    else:
        return None, address

fix_address.count_addresseses = {}
fix_address.address_stop_skipping = {}
