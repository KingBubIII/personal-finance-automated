# check for a accepted answer
def valid_YN_response(input):
    # check for yes or no variations
    if input in ["YES", "Y", "yes", "y", "NO", "N", "no", "n"]:
        return True
    else:
        return False

def user_confirmed(input):
    if input in ["YES", "Y", "yes", "y"]:
        return True
    elif ["NO", "N", "no", "n"]:
        return False