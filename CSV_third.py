from pathlib import Path

def generate_cvs_file(request_responses_list):
    
    data_folder = Path("./../output")
    file_to_open = data_folder / "req_res.csv"
    
    csv_file = open(file_to_open,"w")
    
    first_line = '00 - REQUESTS,00 - RESPONSES\n'
    csv_file.write(first_line)
    
    unsorted_list = []
    for request_responses in request_responses_list:
        
        req = request_responses.request
        responses = ''
        
        for resp in request_responses.responses:
            responses += resp + ','
            
        line = req + ',' + responses[:-1] + '\n'
        
        unsorted_list.append(line)
        
        
        
        
    unsorted_req_res_set = list(set(unsorted_list))  
      
    
    sorted_req_resp_list = sorted(unsorted_req_res_set)
    
    for line in sorted_req_resp_list:
        csv_file.write(line)
        
     
    #===========================================================================
    # for line in unsorted_list:
    #     csv_file.write(line)
    #===========================================================================
            
            
    csv_file.close()
    
if __name__ == "__main__":
    pass
