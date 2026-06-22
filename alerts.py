#This file will be about if conditions are meet to send an alret



def check_alert(symbol, old_price, new_price, threshold):

    difference = ((new_price - old_price) / old_price) * 100

    if  (-(threshold) > difference):

        print(symbol, " went down by: ", round(difference, 2), "%")

    elif(difference > threshold):

        print(symbol, " went up by: ", round(difference, 2), "%")

    else:

        return