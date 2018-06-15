def parse_form_response(main_question, main_answer, base_url):

    parsed_question=[]
    parsed_answer={}
    media_folder =''
    


    def append_row( question_name, question_label, question_type, answer_dict):
    
        if question_name in answer_dict:
            if question_type == 'note':
                answer=''
                
            elif question_type == 'photo':
                answer = 'http://'+base_url+'/media/'+ media_folder +'/attachments/'+ answer_dict[question_name]
                
            elif question_type == 'audio' or question_type == 'video':
                answer = 'http://'+base_url+'/media/'+ media_folder +'/attachments/'+ answer_dict[question_name]
                
            else:
                answer=answer_dict[question_name]

        else:
            answer=''
        
        parsed_question.append({'question_name':question_name, 'question_label':question_label})
        parsed_answer[question_name]=answer

    def parse_repeat( r_object):
        
        r_question = r_object['name']
        if r_question in main_question:
            for r_answer in main_answer[r_question][:1]:
                for first_children in r_object['children']:
                    question_name = r_question+"/"+first_children['name']
                    question_label = question_name
                    
                    if 'label' in first_children:
                        question_label = first_children['label']

                    append_row(question_name, question_label, first_children['type'], r_answer)
        else:
            for first_children in r_object['children']:
                question_name = r_question+"/"+first_children['name']
                question_label = question_name
                
                if 'label' in first_children:
                    question_label = first_children['label']

                append_row(question_name, question_label, first_children['type'], {})

    def parse_group( prev_groupname, g_object):
       
        g_question = prev_groupname+g_object['name']
        for first_children in g_object['children']:
            question_name = g_question+"/"+first_children['name']
            question_label = question_name

            if 'label' in first_children:
                question_label = first_children['label']
            
            append_row(question_name, question_label, first_children['type'], main_answer)
            
            # done at the end because wee want to print group name as well in report.
            if first_children['type'] == 'group':
                parse_group(g_question+"/",first_children)

    def parse_individual_questions():
       
        for first_children in main_question:
            if first_children['type'] == "repeat":
                parse_repeat(first_children)
            elif first_children['type'] == 'group':
                parse_group("", first_children)
            else:
                question_name = first_children['name']
                question_label = question_name

                if 'label' in first_children:
                    question_label = first_children['label']
                
                append_row(question_name, question_label, first_children['type'], main_answer)
    
    parse_individual_questions()

    return parsed_question, parsed_answer
