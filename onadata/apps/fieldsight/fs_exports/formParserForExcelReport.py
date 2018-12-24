def parse_form_response(main_question, main_answer, base_url, media_folder):

    parsed_question=[]
    parsed_answer={}
    repeat_qa={}
    repeat_questions=[]
    

    def append_row(question_name, question_label, question_type, answer_dict, is_repeat=None):
    
        if question_name in answer_dict:
            if question_type == 'note':
                answer=''
                
            elif question_type == 'photo' or question_type == 'audio' or question_type == 'video':
                answer = 'http://'+base_url+'/attachment/medium?media_file='+ media_folder +'/attachments/'+ answer_dict[question_name]
                
            else:
                answer=answer_dict[question_name]

        else:
            answer=''
        if is_repeat:
            return {'question_name':question_name, 'question_label':question_label}, answer
        else:
            parsed_question.append({'question_name':question_name, 'question_label':question_label})
            parsed_answer[question_name]=answer

    def parse_repeat_group( prev_groupname, g_object):
        question_questions_ = []
        g_question = prev_groupname+g_object['name']
        for first_children in g_object['children']:
            question_name = g_question+"/"+first_children['name']
            question_label = question_name

            if 'label' in first_children:
                question_label = first_children['label']
            if first_children['type'] == 'group':
                group_questions = parse_repeat_group(g_question+"/",first_children)
                repeat_questions_.extend(group_questions)
            # get all answers form all repeted and generate new answer list to send it to re parse.
            # elif first_children['type'] == 'repeat':
            #     parse_repeat(g_question+"/",first_children, answers.get('question_name', []))

            else:
                repeat_questions_.append({'question_name':question_name, 'question_label':question_label})
    
        return questions

    def parse_repeat( prev_groupname, g_object, answers):
        
        g_question = prev_groupname+g_object['name']
        repeat_questions_ = []
        
        for first_children in g_object['children']:
            question_name = g_question+"/"+first_children['name']
            question_label = question_name
            

            if first_children['type'] == 'group':
                group_question=parse_repeat_group( g_question+"/", first_children)
                repeat_questions_.extend(group_questions)


            elif first_children['type'] == 'repeat':
                pass

            else:
                if 'label' in first_children:
                    question_label = first_children['label']
                
                repeat_questions_.append({'question_name':question_name, 'question_label':question_label})
            
            
        repeat_qa[g_question] = {'questions': repeat_questions_, 'answers': answers}
        repeat_questions.append({'g_question':repeat_questions})

    def parse_group( prev_groupname, g_object, answers):
       
        g_question = prev_groupname+g_object['name']
        for first_children in g_object['children']:
            question_name = g_question+"/"+first_children['name']
            question_label = question_name

            if 'label' in first_children:
                question_label = first_children['label']
            if first_children['type'] == 'group':
                parse_group(g_question+"/", first_children, answers)

            elif first_children['type'] == 'repeat':
                parse_repeat(g_question+"/", first_children, answers.get(first_children['name'], []))

            else:
                append_row(question_name, question_label, first_children['type'], answers)
             

    def parse_individual_questions():  
        for first_children in main_question:
            if first_children['type'] == "repeat":
                parse_repeat("", first_children, main_answer.get(first_children['name'], []))
            elif first_children['type'] == 'group':
                parse_group("", first_children, main_answer)
            else:
                question_name = first_children['name']
                question_label = question_name

                if 'label' in first_children:
                    question_label = first_children['label']
                
                append_row(question_name, question_label, first_children['type'], main_answer)
    
    parse_individual_questions()

    return parsed_question, parsed_answer, repeat_qa
