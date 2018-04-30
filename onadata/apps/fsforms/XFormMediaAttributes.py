
def get_questions_and_media_attributes(json):

    questions=[]
    media_attributes=[]
    
    def parse_repeat(r_object):
        r_question = r_object['name']
        for first_children in r_object['children']:
            question = r_question+"/"+first_children['name']
            if first_children['type'] in ['photo', 'audio', 'video']:
                media_attributes.append(question)
                questions.append(question)
            else:
                questions.append(question)

    def parse_group(prev_groupname, g_object):
        g_question = prev_groupname+g_object['name']

        for first_children in g_object['children']:
            question_name = first_children['name']
            question_type = first_children['type']
            
            if question_type == 'group':
                parse_group(g_question+"/",first_children)
                continue

            question = g_question+"/"+first_children['name']
            if question_type in ['photo', 'audio', 'video']:
                media_attributes.append(question)
                questions.append(question)
            else:
                questions.append(question)


    def parse_individual_questions(parent_object):
        for first_children in parent_object:
            if first_children['type'] == "repeat":
                parse_repeat(first_children)

            elif first_children['type'] == 'group':
                parse_group("",first_children)
            
            else:
                if first_children['type'] in ['photo', 'video', 'audio']:
                    question = first_children['name']
                    media_attributes.append(question)
                else:
                    questions.append(question)

    
    parse_individual_questions(json)
    return questions, media_attributes