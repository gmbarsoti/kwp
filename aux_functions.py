from pathlib import Path

def fileLines(path_to_folder, file_name):
    '''return a list with all lines of a txt file'''
    #data_folder = Path("C:/Users/155 X-MX/Desktop/Preenche Servicos")
    data_folder = Path(path_to_folder)
    file_to_open = data_folder / file_name
     
    f = open(file_to_open,"r")
     
    if not file_to_open.exists():
        print("Oops, file doesn't exist!")
    #===========================================================================
    # else:
    #     print(file_name)
    #     print("Yay, the file exists!")
    #===========================================================================
         
    # Getting all lines    
    all_lines = f.readlines()
    #print('lines len: ', str(len(all_lines)))
    return all_lines

def list_ended(list_to_test, list_index):
    if list_index < len(list_to_test):
        return False
    else:
        return True

def is_a_request(line):
    request_response_id = line[2][0]
    requests_values = ['0','1','2','3','8','9','A','B']
    if request_response_id in requests_values:
        return True
    else:
        return False

def is_a_response(line):
    return not is_a_request(line)

def is_negative_response(response):    
    if response[2][0:2] == '7F':
        return True
    else:
        return False
        
def is_response_pending(response):
    if response[2][-3:-1] == '78':
        return True
    else:
        return False