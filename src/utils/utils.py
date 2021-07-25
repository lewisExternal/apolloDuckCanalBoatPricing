from datetime import datetime

def get_time_stamp():

    # current date and time
    now = datetime.now()
    timestampStr = now.strftime("%d-%m-%Y %H:%M:%S")
    
    return timestampStr

def get_file_name_time_stamp():

    # current date and time
    now = datetime.now()
    timestampStr = now.strftime("%d%m%Y%H%M%S")
    
    return timestampStr