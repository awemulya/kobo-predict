
types = {
    0 : type0,
    1 : type1,
    2 : type2,
    3 : type3,
    4 : type4,
    5 : type5,
    6 : type6,
    7 : type7,
    8 : type8,
    9 : type9,
    10 : type10,
    11 : type11,
    12 : type12,
    13 : type13,
    14 : type14,
    15 : type15,
    16 : type16,
    17 : type17,
    18 : type18,
    19 : type19,
    20 : type20,
    21 : type21,
    22 : type22,
    23 : type23,
    24 : type24,
    25 : type25,
    26 : type26,
    27 : type27,
    28 : type28,
    29 : type29,
    30 : type30,
    31 : type31,
    32 : type32,
    33 : type33,
    37 : type37,
    38 : type38,
    39 : type39,
    40 : type40,
    412: type412,
    421: type421,
    422: type422,
    429: type429,
    423: type430,
    432 : type432,
}


def type0(data):
    content = data.source_name +' joined ' + data.event_name + ' as an Organization Admin.'
    return content

def type1(data):
    content = data.source_name +' joined ' + data.get_event_name + ' as an Organization Admin.'
    return content


def type2(data):
    content =  data.source_name +' was added as the Project Manager of ' + data.get_event_name + ' by ' + data.get_extraobj_name + '.'
    return content


def type3(data):
    content =  data.source_name +' was added as Reviewer of ' + data.get_event_name + ' by ' + data.get_extraobj_name + '.'
    return content


def type4(data):
    content =  data.source_name +' was added as Site Supervisor of ' + data.get_event_name + ' by ' + data.get_extraobj_name + '.'
    return content


def type5(data):
    content =  data.source_name +' was assigned as an Organization Admin in ' + data.get_event_name + '.'
    return content

def type6(data):
    content =  data.source_name +' was assigned as a Project Manager in ' + data.get_event_name + ' by ' + data.get_extraobj_name + '.'
    return content

def type7(data):
    content =  data.source_name +' was assigned as a Reviewer in ' + data.get_event_name + '.'
    return content

def type8(data):
    content =  data.source_name +' was assigned as a Site Supervisor in ' + data.get_event_name + '.'
    return content


def type9(data):
    content =  data.source_name +' created a new organization named ' + data.get_event_name + '.'
    return content



def type10(data):
    content =  data.source_name +' created a new project named ' + data.get_event_name + '.'
    return content



def type11(data):
    content =  data.source_name +' created a new site named ' + data.get_event_name + ' in Project named ' + data.get_extraobj_name + '.'
    return content


def type12(data):
    
    content =  data.source_name +' '+ data.extra_message +' in ' + data.get_event_name + '.'
    
    return content



def type13(data):
    content =  data.source_name +' changed the details of organization named ' + data.get_event_name + '.'
    return content
       

def type14(data):
    content =  data.source_name +' changed the details of project named ' + data.get_event_name + '.'
    return content
 

def type15(data, detail=false):
    content =  data.source_name +'</a></b> changed the details of site named <b><a href="' +  data.get_event_url + '">' + data.get_event_name + '.'
    if (data.extra_json && detail):
        const updated = data.extra_json
        content += Object.keys(updated).map(
            key => '<li style="margin-left:60px" ><b>' + updated[key].label + '</b> was updated from <b>' + (updated[key].data[0].length == 0 ? '<i>blank</i>' : updated[key].data[0]) + '</b> to <b>' + (updated[key].data[1].length == 0 ? '<i>blank</i>' : updated[key].data[1]) + '</b>.</li>',
        ).join(' ') + '</ul></div>'
    
    return content
   

def type16(data):
    formdetail = data.get_event_name.split("form")
    level = "site"
    if data.extra_message == "project":
        level="project" 
    content =  data.source_name +' submitted a response for '+ formdetail[0] +'form ' + formdetail[1] + ' in '+ level +' ' + data.get_extraobj_name+'.'
    return content
   

def type17(data):
    formdetail = data.get_event_name.split("form")
    level = "site"
    if data.extra_message == "project":
        level="project" 
    content =  data.source_name +' reviewed a response for '+ formdetail[0] +'form ' + formdetail[1]+' in '+ level +' ' + data.get_extraobj_name+'.'
    return content
   

def type18(data):
    formdetail = data.get_event_name.split("form")  
    content =  data.source_name +' assigned a new '+ formdetail[0] +'form ' + formdetail[1]+' in project ' + data.get_extraobj_name+'.'
    return content
   

def type19(data):
    formdetail = data.get_event_name.split("form")
    content =  data.source_name +' assigned a new '+ formdetail[0] +'form ' + formdetail[1]+' in site ' + data.get_extraobj_name+'.'
    return content
   

def type20(data):
    content =  data.source_name +' edited ' + data.get_event_name + ' form.'
    return content


def type21(data):
    if(data.source_uid == user_id):
        content = "<b>TASK INFO : </b>"+data.extra_message + ' of organization <a href="' +  data.get_event_url + '"><b>' + data.get_event_name + '</a></b> were created.'
    else:
        content =  data.source_name +'</a></b> created '+ data.extra_message +' of organization <b><a href="' +  data.get_event_url + '">' + data.get_event_name + '.'
    return content


def type22(data):
    if(data.source_uid == user_id):
        content = "<b>TASK INFO : </b>"+data.extra_message + ' of project <a href="' +  data.get_event_url + '"><b>' + data.get_event_name + '</a></b> were created.'
    else:
        content =  data.source_name +'</a></b> created <b>'+ data.extra_message +' of project <b><a href="' +  data.get_event_url + '">' + data.get_event_name + '.'
    
    return content


def type23(data):
    content = "<b>TASK INFO : </b>"+data.extra_message + ' in <a href="' +  data.get_event_url + '"><b>' + data.get_event_name + '.'
    return content


def type24(data):
    content =  data.source_name +' was added in ' + data.get_event_name + ' by ' + data.get_extraobj_name + '.'
    return content



def type25(data):
    content =  data.source_name +' was added as Donor of ' + data.get_event_name + ' by ' + data.get_extraobj_name + '.'
    return content



def type26(data):
    content =  data.source_name +' was added as the Project Manager in '+ data.extra_message +' projects of ' + data.get_event_name + ' by ' + data.get_extraobj_name + '.'
    return content


def type27(data):
    content =  data.source_name +' was added as Reviewer in '+ data.extra_message +' sites of ' + data.get_event_name + ' by ' + data.get_extraobj_name + '.'
    return content



def type28(data):
    content =  data.source_name +' was added as Site Supervisor in '+ data.extra_message +' sites of ' + data.get_event_name + ' by ' + data.get_extraobj_name + '.'
    return content



def type29(data):
    content = 'Project Sites import from ' + data.get_extraobj_name + ' has completed successfully in project ' + data.get_event_name + '.'
    return content



def type30(data):
    content = data.extra_message + ' ' + data.get_extraobj_name + ' completed successfully in project ' + data.get_event_name + '.' 
    return content


def type31(data):
    var formdetail = data.get_event_name.split("form")
    var level = "site"
    if data.extra_message == "project":
        level="project" 
    content =  data.source_name +' edited a response in '+ formdetail[0] +'form ' + formdetail[1] + ' in '+ level + ' ' + data.get_extraobj_name+'.'
    return content


def type32(data):
    content = data.extra_message + ' ' + data.get_extraobj_name + ' has successfully been completed.' 
    return content



def type33(data):
    var formdetail = data.get_event_name.split("form")
    content =  data.source_name +' deleted a response submitted by '+ data.extra_json['submitted_by'] +' in '+ formdetail[0] +'form ' + formdetail[1] + ' in '+ data.extra_message +' ' + data.get_extraobj_name+'.'
    return content


def type37(data):
    content =  data.source_name +' was added as the Region Reviewer in region ' + data.get_event_name + ' by ' + data.get_extraobj_name + '.'
    return content


def type38(data):
    content =  data.source_name +' was added as the Region Supervisor in region ' + data.get_event_name + ' by ' + data.get_extraobj_name + '.'
    return content

def type39(data):
    content =  data.source_name +' was added as the Region Reviewer in ' + data.extra_message + ' of ' + data.get_event_name + ' by ' + data.get_extraobj_name + '.'
    return content


def type40(data):
    content =  data.source_name +' was added as the Region Supervisor in ' + data.extra_message + ' of ' + data.get_event_name + ' in ' + data.get_extraobj_name + '.'
    return content




# // ----------------Errors -------------------

# def type412(data):
#     var errormsg=data.extra_message
#     var messages = errormsg.split("@error")
#     console.log(messages)
#     var readableerror = ""
#     if (messages.length > 1):

#         errors = messages[1].split("DETAIL:")
#         if(errors.length > 1):
#             readableerror = errors[1]
        
#         else:
#             readableerror = errors[0]  
        

    
#     else:
#         readableerror = messages[0]
    
#     console.log(readableerror)
#     content = 'Bulk upload of ' + messages[0] + ' has <span style="color:maroon""><b>failed</b></span> in project <a href="' +  data.get_event_url + '"><b>' + data.get_event_name + '. <b>Error:  </b>'+readableerror
#     return content


# def type421(data):
#     content = 'Multi Role assign for ' + data.extra_message + ' has <span style="color:maroon"><b>failed</b></span> in organization <a href="' +  data.get_event_url + '"><b>' + data.get_event_name + '.'
#     return content


# def type422(data):
#     content = data.extra_message + ' has <span style="color:maroon"><b>failed</b></span> in project <a href="' +  data.get_event_url + '"><b>' + data.get_event_name + '.'
#     return content


# def type429(data):
#     content = 'Project Sites import from <a href="' +  data.get_extraobj_url + '"><b>' + data.get_extraobj_name + '</a></b> has <span style="color:maroon"><b>failed</b></span> in project <a href="' +  data.get_event_url + '"><b>' + data.get_event_name + '.'
#     return content


# def type430(data):
#     content = data.extra_message + '<a href="' +  data.get_extraobj_url + '"><b>' + data.get_extraobj_name + '</a></b> has <span style="color:maroon"><b>failed</b></span> in project <a href="' +  data.get_event_url + '"><b>' + data.get_event_name + '.'
#     return content


# def type432(data):
#     content = data.title + ' <a href="' +  data.get_event_url + '"><b>' + data.get_event_name + '</a></b></a></b> has <span style="color:maroon"><b>failed</b></span>. ' + data.extra_message 
#     return content





  







