from subprocess import run, PIPE
from pathlib import Path
import xml.etree.ElementTree as ET
import os
import shutil
import copy
from CSV_third import generate_cvs_file

from request_and_responses import get_communications

#from request_responses_classes import captured_config


def cap_files():
    ''' Return a list with all path to cap files from a specific directory'''
    
    if not os.path.isdir("./../cap_files"):
        print("Missing cap_file directory...")
        print("Missing captured files...")
        print("Creating directory cap_files...")
        os.makedirs("./../cap_files")
   
    all_itens_on_directory = os.listdir("./../cap_files")
    all_cap_path = []
    
    for item in all_itens_on_directory:
        path_to_check = "./../cap_files/" + item
        if os.path.isfile(path_to_check):
            all_cap_path.append(item)
    
    
    return all_cap_path


def generate_xml(cap_file):
    
    root_path = Path("./")
    program_path = root_path / "ProtocolAnalyzerSaveXml.exe"
    
    
    cap_files_path = Path("./../cap_files/")
    cap_path = cap_files_path / cap_file
    
    run([str(program_path),str(cap_path)], stdout=PIPE)


def move_xml_files():
    if not os.path.isdir("./../cap_files/xml_files"):
        print("Missing xml_files directory...")
        print("Missing xml files...")
        print("Creating directory xml_files...")
        os.makedirs("./../cap_files/xml_files")
            
    dir_files = os.listdir("./../cap_files")
    
    cwd = os.getcwd()
    above_dir = os.path.dirname(cwd)
    
    data_directory = Path('./cap_files')
    cap_full_path = above_dir + '\\' + str(data_directory) + '\\'
     
    data_directory = Path("./cap_files/xml_files/")
    xml_full_path = above_dir + '\\' + str(data_directory)+ '\\'
    
    for item in dir_files:
        if item[-3:] == "xml":
            #shutil.move("./../cap_files/" + item, "./../cap_files/xml_files/" + item)
            shutil.move(cap_full_path + item, xml_full_path + item)

def xml_files():
    ''' Return a list with all path to xml files from a specific directory'''
   
    all_cap_path = os.listdir("./../cap_files/xml_files")
    return all_cap_path        

#got from stackoverflow
def clean_path(path):
    path = str(path).replace('/',os.sep).replace('\\',os.sep)
    if os.sep == '\\' and '\\\\?\\' not in path:
        # fix for Windows 260 char limit
        relative_levels = len([directory for directory in path.split(os.sep) if directory == '..'])
        cwd = [directory for directory in os.getcwd().split(os.sep)] if ':' not in path else []
        path = '\\\\?\\' + os.sep.join(cwd[:len(cwd)-relative_levels]\
                         + [directory for directory in path.split(os.sep) if directory!=''][relative_levels:])
    return path


def xml_treatment(xml_file_name):
    
    # list to store communication lines
    com_list = []
    # list to store one communication
    one_com_dict = {}        
    
    #print("Parsing XML file: ", xml_file_name)
    
    data_folder = Path("./../cap_files/xml_files/")
    file_path = data_folder /  xml_file_name
    c_path = clean_path(file_path)
    tree = ET.parse(c_path)
    root = tree.getroot()
    
    #===========================================================================
    # print(xml_file_name)
    # node = root.find('Config').find('CAN').find('Filter').findall('Item')
    # for info_addr in node:
    #     print(info_addr.find('Id').text)
    # 
    #===========================================================================
    
    xml_dict = {}
    config_node = root.find('Config')
    
    #verify error if xml file does not have this node
    if config_node == None:
        return xml_dict, com_list
   
    for iterator_note in config_node[1].iter():
        if not str(iterator_note.text) == "None":
            xml_dict[iterator_note.tag] = iterator_note.text
            
    
    #verify error if xml file does not have this node
    total_lines_node = config_node.find("Total")
    if total_lines_node == None:
        return xml_dict, com_list
    
    # Number of lines
    xml_dict["Total_lines"] = total_lines_node.text
    
    # Get communication lines
    
    data_node = root.find("Data")

    #verify error if xml file does not have this node
    if data_node == None:
        return xml_dict, com_list
    
    for item_node in data_node:
        for child_node in item_node:
            one_com_dict[child_node.tag] = child_node.text
        com_list.append(dict(one_com_dict)) 
        
    return xml_dict, com_list

def mount_lines(xml_file_name,request_responses_list):
    try:
        print('file: ' + xml_file_name + '\n\n')
        data_folder = Path("./../cap_files/xml_files/")
        file_path = data_folder /  xml_file_name
        c_path = clean_path(file_path)
        tree = ET.parse(c_path)
        
        #xml root
        root = tree.getroot()
        
        #Time got when was did the capture
        base_time = int(root.find('Config').find('Serial').find('Time').text)
        
        #build a function to get the best the biggest time between an given interval 
        #using interval from 15000 to 5000
        
        
        
        # iterator to go in all tags <Item> in the xml file
        bytes_iterator = root.iter("Item")
        
        #list to store the tuples containing byte and time 
        byte_n_time = []
        
        lower_limit_interval = 6500
        upper_limit_interval = 6800
        division_time = base_time
        #iterating through xml and building a list with all byte and time tuples
        for item_elem in bytes_iterator:
            #if ( int( '0x' + b.find( "Data").text,16) > int(0x7F) ) and (int('0x' + b.find("Data").text,16) < int(0x90) ):
            #erase the list if the comment 'Error: Framing Error' is found
            
            #if the frame has an error message the list is been cleaned, maybe it is not the most correct to do
            #the list will contain only data after the last frame that had an error message
            if (not item_elem.find("Comment") == None): # check if node exists
                if item_elem.find("Comment").text == 'Error: Framing Error':
                    del byte_n_time[:]
            
            if (not item_elem.find("Data") == None) and (not item_elem.find("Time") == None): 
                byte_n_time.append((item_elem.find("Data").text,item_elem.find("Time").text))
                if (int(item_elem.find("Time").text) > lower_limit_interval) and (int(item_elem.find("Time").text) < upper_limit_interval):
                    division_time = int(item_elem.find("Time").text)
                    
                    
                    
            #=======================================================================
            # if item_elem.find("Comment").text == 'Error: Framing Error':
            #     del byte_n_time[:]
            # else:
            #     byte_n_time.append((item_elem.find("Data").text,item_elem.find("Time").text))
            #     if (int(item_elem.find("Time").text) > lower_limit_interval) and (int(item_elem.find("Time").text) < upper_limit_interval):
            #         division_time = int(item_elem.find("Time").text)
            #=======================================================================
                    
                    
                    
        
        #printing a line by the scanner communication and other line by the module communication
        
        
        f = open("all_lines.txt",'a+')
        
        #===========================================================================
        # communication_line = []
        # communication_list = []
        #===========================================================================
        data_bytes = []
        
        #control to remove invalid bytes at communication beginning
        pop_byte = True
        
        
        # address to harded coded to test
        ECU_addr = '11'
        SCN_addr = 'F1'
        
        
        
        
        #Removing bytes that are lower than 81 to start with a byte that is a size byte - size bytes are bigger than 80 
        while pop_byte:
            byte_to_evaluate = byte_n_time[0][0]
            #time_to_evaluate = byte_n_time[0][1]
            supposed_ECU_addr = byte_n_time[1][0]
            supposed_SCN_addr = byte_n_time[2][0]
            
            # if lower than 81 pop it
            if byte_to_evaluate  < '81':
                byte_n_time.pop(0)
            # if bigger check if time is a time to change frame byte - base_time
            else:
                # if time is bigger than base_time, the byte_to_evaluate is considered a size byte, so get out from loop
                # else pop this byte
                if supposed_ECU_addr == ECU_addr and supposed_SCN_addr == SCN_addr:  
                    pop_byte = False
                else:
                    byte_n_time.pop(0)
                    
                #===================================================================
                # if time_to_evaluate >= base_time:
                #     pop_byte = False
                # else:
                #     byte_n_time.pop(0)
                #===================================================================
        
        #######
        
        hex_80_reference = int('80',16)
        size_byte = byte_n_time[0][0] #first size byte
        
        #first data length, difference between 0x80 and size byte 
        data_length = int(size_byte,16) - hex_80_reference
        
        #request data limit inferior and limit superior
        req_limit_inferior = 3 # skip the first three positions (size, target and source bytes)
        req_limit_superior = req_limit_inferior + data_length
        
        #bool to know if there is still data to get from byte_n_time list
        there_is_data = True
        
        
        final_list = []
        
        # going through list of data byte_n_time
        while there_is_data:
        
            # Stop loop if the last frame is incomplete
            if len(byte_n_time) <= req_limit_inferior:
                    there_is_data = False
            else:
                #list of data with byte and its time per position
                data_bytes_n_time = byte_n_time[req_limit_inferior:req_limit_superior]
    
                #source address
                source_addr = byte_n_time[req_limit_inferior-1][0] + '.'
                
                #data length string
                data_lengh_string = str(data_length) + '.'   
                              
                #getting just the data from list with bytes and its bytes
                data_string = ''
                for data_byte in data_bytes_n_time:
                    data_string += data_byte[0] + '.'
                    data_bytes.append(data_byte[0])
                
                #final_list element
                f_l_element = [source_addr,data_lengh_string,data_string]
                
                final_list.append(copy.deepcopy(f_l_element))
                
                #=======================================================================
                # #appending data bytes from frame to communication list
                # communication_list.append(copy.deepcopy(data_bytes))
                #=======================================================================
                
                #clearing auxiliary list data_bytes
                data_bytes.clear()
                
                # Stop loop if there is no more data to check
                if len(byte_n_time) == req_limit_superior + 1:
                        there_is_data = False
                else:
                    
                    #data limits update
                    size_byte_position = req_limit_superior + 1 # 1 is to skip checksum byte
                    size_byte = byte_n_time[size_byte_position][0] # getting size byte
                    
                    req_limit_inferior = req_limit_inferior + data_length + 4 # the 4 is to skip bytes check sum, size, target and source
                    
                    data_length = int(size_byte,16) - hex_80_reference # updating data length to set correct superior limit position
                    
                    req_limit_superior = req_limit_inferior + data_length # updating superior limit
                  
        
    #===============================================================================
    #     
    #     for b_n_t in byte_n_time:
    #         if(int(b_n_t[1]) <= division_time):
    #             communication_line.append(b_n_t[0])
    #             f.write(b_n_t[0]+'.')
    #             print(b_n_t[0]+'.', end='')
    #         else:
    #             communication_list.append(copy.deepcopy(communication_line))
    #             #if was appended a empty element, pop it
    #             if communication_list[-1] == []:
    #                 communication_list.pop()
    #             
    #             #===================================================================
    #             # for i in communication_line:
    #             #     print(i)
    #             #     f.write(i)
    #             #===================================================================
    #             communication_line.clear()
    #             f.write('\n'+ b_n_t[0]+'.')
    #             print('\n'+ b_n_t[0]+'.', end='')
    #             #inserting the first byte ex: 81
    #             communication_line.append(b_n_t[0])
    # 
    #     f.close()
    #===============================================================================
    
        # put communication in final list format
        
        
        #===========================================================================
        # # final_list elements: ['source_id','data_length','data']
        # # CAN Ex: ['7D3.','3.','22.3B.02.']
        # final_list = []
        # for one_communication in communication_list:
        #     if len(one_communication)>=5:    
        #         source_id = str(one_communication[2]) + '.'
        #         data_length = str(len(one_communication[3:-1])) + '.'
        #         data = one_communication[3:-1]
        #         #if(not len(data) < 2):
        #         data_str = ''
        #         for byte in data:
        #             data_str += str(byte) + '.'
        #         
        #         final_list_element = [source_id, data_length, data_str]
        #         final_list.append(final_list_element)
        # 
        #===========================================================================
        
        
        
        
        get_communications(final_list, request_responses_list)  
        if None in request_responses_list:
            request_responses_list.remove(None)
            
        return request_responses_list
        #===========================================================================
        # while not line_build:
        #     if byte_time < base_time:
        #         com_line += byte
        #     else:
        #         com_line += '\n'
        #         line_build = True
        # 
        # lines_to_txt.append(com_line)
        #===========================================================================
    
        
    except Exception as e: 
        print("ERROR: \n"+str(e))
        print("File not analysed, please check it manually:\n"+xml_file_name[:-3]+"ctec\n")
        return []



def cap_to_txt_xml():
         
    all_cap_files = cap_files()
    
    # Generating all XML files from cap files
    print("Creating XML files...")
    for cap_file in all_cap_files:
        generate_xml(cap_file)
        
    # Moving files to xml directory
    move_xml_files()
     
    # Create a .txt file from each xml file
    
    all_xml_files =  xml_files()
    
    
         
    request_responses_list = []
    for file_xml in all_xml_files:
        mount_lines(file_xml,request_responses_list)
    
                
    generate_cvs_file(request_responses_list)        
     
if __name__ == "__main__":
    
    cap_to_txt_xml()