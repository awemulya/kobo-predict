class Test():
    def log_type0(self, data):
        return data.source.first_name + ' ' + data.source.last_name +' joined ' + data.event_name + ' as an Organization Admin.'
        

    def log_type1(self, data):
        return data.source.first_name + ' ' + data.source.last_name +' joined ' + data.event_name + ' as an Organization Admin.'
        


    def log_type2(self, data):
        return data.source.first_name + ' ' + data.source.last_name +' was added as the Project Manager  by ' + data.extra_obj_name + '.'
        


    def log_type3(self, data):
        return data.source.first_name + ' ' + data.source.last_name +' was added as Reviewer of ' + data.event_name + ' by ' + data.extra_obj_name + '.'
        


    def log_type4(self, data):
        return data.source.first_name + ' ' + data.source.last_name +' was added as Site Supervisor of ' + data.event_name + ' by ' + data.extra_obj_name + '.'
        


    def log_type5(self, data):
        return data.source.first_name + ' ' + data.source.last_name +' was assigned as an Organization Admin in ' + data.event_name + '.'
        

    def log_type6(self, data):
        return data.source.first_name + ' ' + data.source.last_name +' was assigned as a Project Manager in ' + data.event_name + ' by ' + data.extra_obj_name + '.'
        

    def log_type7(self, data):
        return data.source.first_name + ' ' + data.source.last_name +' was assigned as a Reviewer in ' + data.event_name + '.'
        

    def log_type8(self, data):
        return data.source.first_name + ' ' + data.source.last_name +' was assigned as a Site Supervisor in ' + data.event_name + '.'
        


    def log_type9(self, data):
        return data.source.first_name + ' ' + data.source.last_name +' created a new organization named ' + data.event_name + '.'
        



    def log_type10(self, data):
        return data.source.first_name + ' ' + data.source.last_name +' created a new project named ' + data.event_name + '.'
        



    def log_type11(self, data):
        return data.source.first_name + ' ' + data.source.last_name +' created a new site named ' + data.event_name + ' in Project named ' + data.extra_obj_name + '.'
        


    def log_type12(self, data):
        return data.source.first_name + ' ' + data.source.last_name +' '+ data.extra_message +' in ' + data.event_name + '.'
        



    def log_type13(self, data):
        return data.source.first_name + ' ' + data.source.last_name +' changed the details of organization named ' + data.event_name + '.'
        
           

    def log_type14(self, data):
        return data.source.first_name + ' ' + data.source.last_name +' changed the details of project named ' + data.event_name + '.'
        
     

    def log_type15(self, data, detail=False):
        return data.source.first_name + ' ' + data.source.last_name +' changed the details of site named ' + data.event_name + '.'
        sub_contents = []
        if (data.extra_json and detail) :
            updated = data.extra_json
            for key, value in updated.items():
                sub_contents.append(updated[key].label + 'was updated from' + ('blank' if updated[key].data[0] == '' else updated[key].data[0]) + ' to ' + ('blank' if updated[key].data[1] == '' else updated[key].data[1]) + '.')

        , sub_contents
       

    def log_type16(self, data):
        formdetail = data.event_name.split("form")
        return data.source.first_name + ' ' + data.source.last_name +' submitted a response for '+ formdetail[0] +'form ' + formdetail[1] + ' in ' + data.extra_obj_name + '.'
        
       

    def log_type17(self, data):
        formdetail = data.event_name.split("form")
        return data.source.first_name + ' ' + data.source.last_name +' reviewed a response for '+ formdetail[0] +'form ' + formdetail[1]+' in ' + data.extra_obj_name + '.'
        
       

    def log_type18(self, data):
        formdetail = data.event_name.split("form")  
        return data.source.first_name + ' ' + data.source.last_name +' assigned a new '+ formdetail[0] +'form ' + formdetail[1]+' in project ' + data.extra_obj_name + '.'
        
       

    def log_type19(self, data):
        formdetail = data.event_name.split("form")
        return data.source.first_name + ' ' + data.source.last_name +' assigned a new '+ formdetail[0] +'form ' + formdetail[1]+' in site ' + data.extra_obj_name + '.'
        
       


    def log_type20(self, data):
        return data.source.first_name + ' ' + data.source.last_name +' edited ' + data.event_name + ' form.'
        


    def log_type21(self, data):
        return data.source.first_name + ' ' + data.source.last_name +' created '+ data.extra_message +' of organization ' + data.event_name + '.'
        
        


    def log_type22(self, data):
        return data.source.first_name + ' ' + data.source.last_name +' created '+ data.extra_message +' of project ' + data.event_name + '</a></b>.'    
        


    def log_type24(self, data):
        return data.source.first_name + ' ' + data.source.last_name +' was added in ' + data.event_name + ' by ' + data.extra_obj_name + '.'
        



    def log_type25(self, data):
        return data.source.first_name + ' ' + data.source.last_name +' was added as Donor of ' + data.event_name + ' by ' + data.extra_obj_name + '.'
        



    def log_type26(self, data):
        return  data.source.first_name + ' ' + data.source.last_name +' was added as the Project Manager in '+ data.extra_message +' projects of ' + data.event_name + ' by ' + data.extra_obj_name + '.'
        


    def log_type27(self, data):
        return data.source.first_name + ' ' + data.source.last_name +' was added as Reviewer in '+ data.extra_message +' sites of ' + data.event_name + ' by ' + data.extra_obj_name + '.'
        



    def log_type28(self, data):
        return data.source.first_name + ' ' + data.source.last_name +' was added as Site Supervisor in '+ data.extra_message +' sites of ' + data.event_name + ' by ' + data.extra_obj_name + '.'
        


    def log_type31(self, data):
        formdetail = data.event_name.split("form")
        level= "project" if data.extra_message == "project" else "site" 
        return data.source.first_name + ' ' + data.source.last_name +' edited a response in '+ formdetail[0] +'form ' + formdetail[1] + ' in '+ level +' ' + data.extra_obj_name+'.'
        


    def log_type33(self, data):
        formdetail = data.event_name.split("form")
        return data.source.first_name + ' ' + data.source.last_name +' deleted a response submitted by '+ data.extra_json['submitted_by'] +' in '+ formdetail[0] +'form ' + formdetail[1] + ' in '+ data.extra_message + data.extra_obj_name+'.'
        


    def log_type34(self, data):
        formdetail = data.event_name.split("form")
        return data.source.first_name + ' ' + data.source.last_name +' deleted '+ formdetail[1] +' with '+ str(data.extra_json['submission_count']) +' submissions in ' + data.extra_obj_name + '.'
        


    def log_type36(self, data):
        return data.source.first_name + ' ' + data.source.last_name +' deleted '+ data.extra_message +' named '+ data.event_name +' of '+ data.extra_obj_name +'.'
        


    log_types = {
            0 : log_type0,
            1 : log_type1,
            2 : log_type2,
            3 : log_type3,
            4 : log_type4,
            5 : log_type5,
            6 : log_type6,
            7 : log_type7,
            8 : log_type8,
            9 : log_type9,
            10 : log_type10,
            11 : log_type11,
            12 : log_type12,
            13 : log_type13,
            14 : log_type14,
            15 : log_type15,
            16 : log_type16,
            17 : log_type17,
            18 : log_type18,
            19 : log_type19,
            20 : log_type20,
            21 : log_type21,
            22 : log_type22,
            24 : log_type24,
            25 : log_type25,
            26 : log_type26,
            27 : log_type27,
            28 : log_type28,
            31 : log_type31,
            33 : log_type33,
            34 : log_type34,
            36 : log_type36,
        }



      







