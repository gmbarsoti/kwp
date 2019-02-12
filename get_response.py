from request_responses_classes import response_interface_pack
from aux_functions import list_ended, is_a_response, is_negative_response, is_response_pending, is_a_request


def get_multiple_responses(full_list, list_index, response_interface_obj):
    '''getting responses to the same request if there are more'''
    multiple_responses = True
    
    while multiple_responses:
        
        if list_ended(full_list, list_index):
            # list has ended
            response_interface_obj.responses.append('cap_file_ended')
            multiple_responses = False
            
        else:
            
            line = full_list[list_index]
            # getting last response recorded
            last_response = response_interface_obj.responses[-1]
            # getting first byte of last response 
            previous_first_byte = last_response[0:2]
            # getting current response/request
            res_or_req = line[2]
            # getting first byte of current response/request
            first_byte = res_or_req[0:2]
            
            if is_a_response(line) and (first_byte == previous_first_byte):
                # the next response is also response to the last request
                response_interface_obj.responses.append(res_or_req)
                list_index += 1
            else:
                multiple_responses = False
        
            


def get_response(full_list, list_index):
    
    response_interface_obj = response_interface_pack([],list_index)
    
    if list_ended(full_list, list_index):
        # list has ended
        response_interface_obj.responses.append('cap_file_ended')
        return response_interface_obj
    
    
    line = full_list[list_index]
    
    if not is_a_response(line):
        # request without response
        response_interface_obj.responses.append('no_response_-_the_following_communication_is_also_a_request!')
        return response_interface_obj
    
    # found a response
    response_interface_obj.responses.append(line[2])
    
    list_index += 1 # go to next line
    
    #getting responses to the same request if there are more
    get_multiple_responses(full_list, list_index, response_interface_obj)
            
    
    # skipping negative pending response and tester present communication
    res_or_req = line[2]
    resp_pending = False
    
    if is_negative_response(line):
        if is_response_pending(line):
            # response pending
            resp_pending = True
    
    list_not_ended = True
    
    while resp_pending and list_not_ended:
        # case that response have to wait (response 7F.XY.78 - 78 means response is pending) and skip its tester present communication    
        # list_index += 1 # go to next line
        
        if list_ended(full_list, list_index):
            # list has ended
            response_interface_obj.responses.append('cap_file_ended')
            list_not_ended = False
            
        else:
            
            line = full_list[list_index]
            res_or_req = line[2]

            if res_or_req == '3E.01.' or res_or_req[0:2] == '7F': 
                # ignoring tester present
                list_index += 1 # go to next line
                pass
        
            elif not res_or_req[0:2] == '7F':
                
                #print('Pending response found')
                response_interface_obj.responses.append(res_or_req)
                
                resp_pending = False
                
                list_index += 1
                
                #getting responses to the same request if there are more
                get_multiple_responses(full_list, list_index, response_interface_obj)
            
            
            elif is_a_request(line):
                #print('Pending response not found')
                resp_pending = False
                # request without response
                response_interface_obj.responses.append('no_response_-_the_following_communication_is_also_a_request!')
                # don't go to the next list item        
    
    response_interface_obj.list_index = list_index
    
    return response_interface_obj
