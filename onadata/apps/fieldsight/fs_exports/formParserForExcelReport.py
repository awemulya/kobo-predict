def parse_form_response(main_question, main_answer, base_url, media_folder):

    parsed_question=[]
    parsed_answer={}
    repeated_qa=[]
    repeat_questions=[]
    


    def append_row(question_name, question_label, question_type, answer_dict, is_repeat=None):
    
        if question_name in answer_dict:
            if question_type == 'note':
                answer=''
                
            elif question_type == 'photo':
                answer = 'http://'+base_url+'/attachment/medium?media_file=/'+ media_folder +'/attachments/'+ answer_dict[question_name]
                
            elif question_type == 'audio' or question_type == 'video':
                answer = 'http://'+base_url+'/attachment/medium?media_file=/'+ media_folder +'/attachments/'+ answer_dict[question_name]
                
            else:
                answer=answer_dict[question_name]

        else:
            answer=''
        if is_repeat:
            return {'question_name':question_name, 'question_label':question_label}, answer
        else:
            parsed_question.append({'question_name':question_name, 'question_label':question_label})
            parsed_answer[question_name]=answer

    def parse_repeat( r_object):
        
        r_question = r_object['name']
        if r_question in main_question:
            repeat = 1
            for r_answer in main_answer[r_question]:
                repeated_group = {}
                for first_children in r_object['children']:
                    question_name = r_question+"/"+first_children['name']
                    question_label = question_name
                    
                    if 'label' in first_children:
                        question_label = first_children['label']
                    
                    question, answer = append_row(question_name, question_label, first_children['type'], r_answer, True)
                    if repeat == 1:
                        repeat_questions.append(question)
                        append_row(question_name, question_label, first_children['type'], r_answer)
                    repeat += 1
                    repeated_group[question['question_name']] = answer
                repeated_qa.append(repeated_group)

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

    return parsed_question, parsed_answer, repeat_questions, repeated_qa
