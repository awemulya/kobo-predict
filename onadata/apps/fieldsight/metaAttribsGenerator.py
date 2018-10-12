from .models import Project, Site
from onadata.apps.fsforms.models import FieldSightXF
def generateSiteMetaAttribs(pk):
    metas = []
    site = Site.objects.get(pk=pk)
    project = site.project
    main_project = project.id



    def generate(metas, project_id, metas_to_parse, meta_answer, parent_selected_metas, project_metas):

        for meta in metas_to_parse:
            # if project_metas and meta not in project_metas:
            #     continue
            if meta.get('question_type') == "Link":
                if parent_selected_metas:
                    selected_metas = parent_selected_metas
                else:
                    selected_metas = meta.get('metas')
                if meta.get('project_id') == main_project:
                    continue
                sitenew = Site.objects.filter(identifier = meta_answer.get(meta.get('question_name'), None), project_id = meta.get('project_id'))
                if sitenew and str(sitenew[0].project_id) in selected_metas:
                    answer = meta_answer.get(meta.get('question_name'))
                    sub_metas = []
                    generate(sub_metas, sitenew[0].project_id, selected_metas[str(sitenew[0].project_id)], sitenew[0].site_meta_attributes_ans, selected_metas, sitenew[0].project.site_meta_attributes)
                    metas.append({'question_text': meta.get('question_text'), 'project_id':meta.get('project_id'), 'answer':answer, 'question_type':'Link', 'children':sub_metas})
                    
                else:
                    answer = "No Site Refrenced"
                    metas.append({'question_text': meta.get('question_text'), 'answer':answer, 'question_type':'Normal'})

                    
            else:
                answer=""
                question_type="Normal"

                if meta.get('question_type') == "Form":
                    fxf = FieldSightXF.objects.filter(site_id=site.id, fsform_id=int(meta.get('form_id', "0")))
                    if fxf:
                        sub = fxf[0].project_form_instances.filter(site_id=pk).order_by('-pk')[:1]
                        if sub:

                            sub_answers = sub[0].instance.json
                            answer = sub_answers.get(meta.get('question').get('name') ,'')
                            if meta['question']['type'] in ['photo', 'video', 'audio'] and answer is not "":
                                question_type = "Media"
                                answer = 'http://'+request.get_host()+'/attachment/medium?media_file='+ fxf.xf.user.username +'/attachments/'+answer
                        else:
                            answer = "No Submission Yet."
                    else:
                        answer = "No Form"



                elif meta.get('question_type') == "FormSubStat":
                    fxf = FieldSightXF.objects.filter(site_id=site.id, fsform_id=int(meta.get('form_id', "0")))
                    if fxf:
                        sub_date = fxf[0].getlatestsubmittiondate()
                        if sub_date:
                            answer = "Last submitted on " + sub_date[0]['date'].strftime("%d %b %Y %I:%M %P")
                        else:
                            answer = "No submission yet."
                    else:
                        answer = "No Form"
                else:
                    answer = meta_answer.get(meta.get('question_name'), "")

                metas.append({'question_text': meta.get('question_text'), 'answer':answer, 'question_type':question_type})


    generate(metas, project.id, project.site_meta_attributes, site.site_meta_attributes_ans, None, None)

    return metas
