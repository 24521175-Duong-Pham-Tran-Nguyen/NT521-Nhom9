# Fill the Python code in this file
from test_data import *
from policy import POLICY #change 4

def json_search(key,input_object,role=None): # change 5 

    if role is not None and key in POLICY and role not in POLICY[key]:
   	 return [] #change 6

    ret_val=[] 
    if isinstance(input_object, dict): # Iterate dictionary 
        for k, v in input_object.items(): # searching key in the dict 
            if k == key: 
                temp={k:v} 
                ret_val.append(temp) 
            if isinstance(v, dict): # the value is another dict so repeat 
                ret_val.extend(json_search(key, v, role)) # change 1
            elif isinstance(v, list): # it's a list 
                for item in v: 
                    if not isinstance(item, (str,int)): # if dict or list repeat 
                        ret_val.extend(json_search(key, item, role)) # change 2
    else: # Iterate a list because some APIs return JSON object in a list 
        for val in input_object: 
            if not isinstance(val, (str,int)): 
                ret_val.extend(json_search(key, val,role)) # change 3
    return ret_val 
print(json_search("issueSummary",data,role="viewer"))
#change 7: add role at all recursion
