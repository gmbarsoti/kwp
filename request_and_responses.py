from adjust_list import adjust_list, clean_all_lines
from aux_functions import list_ended, is_a_request, fileLines
from request_responses_classes import request_responses
from get_response import get_response
from os import listdir
from os.path import isfile

def ignoring_initial_responses(full_list, list_index):
    ''' ignoring initial lines that are not requests'''
    found_request = False
    
    while not list_ended(full_list, list_index) and not found_request:
        line = full_list[list_index]
        
        
        if not is_a_request(line):
            #updating list index, going to the next line
            list_index += 1
        else:
            found_request = True
        

            
def req_and_res(full_list):
    """Return a list with all requests and its responses"""
    
    request_responses_list = []
    list_index = 0
    
    # ignoring initial lines that are not requests
    ignoring_initial_responses(full_list, list_index)
    
    while not list_ended(full_list, list_index):
        
        request_response_object = request_responses("",[])
        
        line = full_list[list_index]
        data = line[2]
        
        if is_a_request(line):
            # it is a request
            request_response_object.request = data
            list_index += 1
            
            responses_obj = get_response(full_list, list_index)
            
            list_index = responses_obj.list_index
                
            for response in responses_obj.responses:
                request_response_object.responses.append(response)
            
            request_responses_list.append(request_response_object)
  
        else:
            list_index += 1
            # ignoring initial lines that are not requests
            pass        
             
    return  request_responses_list

def append_response(request, services_occurred_list, req_res_obj, request_responses_list):
    
    elem_pos = services_occurred_list.index(request) # getting position
    
    response = req_res_obj.responses[0] # Just position 0 (Zero) because at this point there is just one response to requests in this list
    
    if not response in request_responses_list[elem_pos].responses:
        request_responses_list[elem_pos].responses.append(response)
    else:
        pass
    
def requests_occurred(request_responses_list):
    '''Return a list with just requests that already occurred'''
    
    occurred_requests_list = []
    
    for req_res_obj in request_responses_list:
        occurred_requests_list.append(req_res_obj.request)
    
    return occurred_requests_list
    

def occurred_cases(req_res_class_list, request_responses_list):
    ''' Append to a received list, occurrences of each request and its responses'''
    
    req_occurred = requests_occurred(request_responses_list) # list to store services that have already been found
    
    for req_res_obj in req_res_class_list:
        
        req = req_res_obj.request # getting just the service
    
        if req in req_occurred: # if request was already found
            
            # appending response if it was not registered yet to its request
            append_response(req, req_occurred, req_res_obj, request_responses_list)
        
        if not req in req_occurred: # if request was not found yet
            req_occurred.append(req) # record this request occurrence
            
            request_responses_list.append(req_res_obj) # store request and response



def get_communications(param_final_list, request_responses_list):        

    #===========================================================================
    #     
    # # Getting all lines from file dados.txt
    # lines = fileLines(path_to_directory_framesCAN, data_txt_file)
    # 
    #===========================================================================
    #===========================================================================
    # # if list is empty
    # if request_responses_list == []:
    #     return 0
    #===========================================================================
    
    #===========================================================================
    # ############################################
    # 
    # # Leaving lines list in a treatable format
    # lines = adjust_list(lines)
    # 
    # # Removing separators in each line
    # # final_list elements: ['source_id','data_length','data']
    # # CAN Ex: ['7D3.','3.','22.3B.02.']
    # final_list = clean_all_lines(lines)
    # 
    # 
    # 
    #===========================================================================
    
    
    
    
    final_list = param_final_list
    
    
    
    
    # Organizing requests and responses in a list
    list_req_and_res = req_and_res(final_list)
    
     
    # Checking if there was communication
    if request_responses_list == 0:
        pass
        print('No communicaiton found in dados.txt file \nfinishing app....')
         
    else:
         
        # Get just one occurrence of each service in communication from dados.txt file
        occurred_cases(list_req_and_res, request_responses_list)
         
    
    
def services_occurrences():
    
    request_responses_list = []
    
    get_communications(request_responses_list)
    
    return request_responses_list

 
if __name__ == "__main__":
     
    services_occurrences()  
