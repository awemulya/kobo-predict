import json
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.platypus import Spacer, SimpleDocTemplate, Table, TableStyle, PageBreak
from reportlab.platypus import Image
from reportlab.lib import colors
from onadata.apps.fsforms.reports_util import get_instaces_for_site_individual_form
from django.db.models import Prefetch
from onadata.apps.fsforms.models import FieldSightXF, FInstance, Site
from reportlab.lib.enums import TA_RIGHT
from reportlab.pdfbase.pdfmetrics import stringWidth
from  reportlab.lib.styles import ParagraphStyle as PS
from  reportlab.platypus.tableofcontents import TableOfContents
styleSheet = getSampleStyleSheet()

class MyDocTemplate(SimpleDocTemplate):
     def __init__(self, filename, **kw):
         self.allowSplitting = 0
         apply(SimpleDocTemplate.__init__, (self, filename), kw)

# Entries to the table of contents can be done either manually by
# calling the addEntry method on the TableOfContents object or automatically
# by sending a 'TOCEntry' notification in the afterFlowable method of
# the DocTemplate you are using. The data to be passed to notify is a list
# of three or four items countaining a level number, the entry text, the page
# number and an optional destination key which the entry should point to.
# This list will usually be created in a document template's method like
# afterFlowable(), making notification calls using the notify() method
# with appropriate data.

     def afterFlowable(self, flowable):
        if flowable.__class__.__name__ == 'Paragraph':
            text = flowable.getPlainText()
            style = flowable.style.name
            if style == 'Heading1':
                 key = 'h1-%s' % self.seq.nextf('heading1')
                 self.canv.bookmarkPage(key)
                 self.notify('TOCEntry', (0, text, self.page, key))
            if style == 'Heading2':
                 key = 'h2-%s' % self.seq.nextf('heading2')
                 self.canv.bookmarkPage(key)
                 self.notify('TOCEntry', (1, text, self.page, key))
                 
            if style == 'Heading3':
                 key = 'h3-%s' % self.seq.nextf('heading3')
                 self.canv.bookmarkPage(key)
                 self.notify('TOCEntry', (2, text, self.page, key))

class MyPrint:


    def __init__(self, buffer, pagesize):
        self.main_answer = {}
        self.question={}
        self.data=[]
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        elif pagesize == 'Letter':
            self.pagesize = letter
        self.width, self.height = self.pagesize
        self.base_url = ''
        self.media_folder = ''
        self.project_name = ''
        self.project_logo = ''


    def create_logo(self, absolute_path):
        image = Image(absolute_path)
        image._restrictSize(2.5 * inch, 2.5 * inch)
        return image

    def _header_footer(self, canvas, doc):
        # Save the state of our canvas so we can draw on it
        canvas.saveState()
        styles = getSampleStyleSheet()
        style_right = ParagraphStyle(name='right', parent=styles['Normal'], fontName='Helvetica',
                fontSize=10, alignment=TA_RIGHT)
        # Header
        
        
        fieldsight_logo = Image('http://' + self.base_url +'/static/images/fs1.jpg')
        fieldsight_logo._restrictSize(1.5 * inch, 1.5 * inch)
        

        # headerleft = Paragraph("FieldSight", styles['Normal'])
        headerright = Paragraph(self.project_name, style_right)

        # w1, h1 = headerleft.wrap(doc.width, doc.topMargin)
        w2, h2 = headerright.wrap(doc.width, doc.topMargin)

        textWidth = stringWidth(self.project_name, fontName='Helvetica',
                fontSize=10) 
        
        fieldsight_logo.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin + 12)
        headerright.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin + 20)

        project_logo = Image('http://' + self.base_url + self.project_logo)
        project_logo._restrictSize(0.4 * inch, 0.4 * inch)
        project_logo.drawOn(canvas, headerright.width + doc.leftMargin -0.5 * inch - textWidth, doc.height + doc.topMargin + 10)
        
        # header.drawOn(canvas, doc.leftMargin + doc.width, doc.height + doc.topMargin +20)
        
        # Footer
        footer = Paragraph('Page no. '+str(canvas._pageNumber), style_right)
        w, h = footer.wrap(doc.width, doc.bottomMargin)
        footer.drawOn(canvas, doc.leftMargin, h + 40)
 
        # Release the canvas
        canvas.restoreState()
    
    def parse_repeat(self, r_object):
        styNormal = styleSheet['Normal']
        styBackground = ParagraphStyle('background', parent=styNormal, backColor=colors.white)
        gnr_question = r_object['name']
        for gnr_answer in self.main_answer[gnr_question]:
            for first_children in r_object['children']:
                question = first_children['name']
                group_answer = self.main_answer[gnr_question]
                question_label = first_children['label']
                if gnr_question+"/"+question in gnr_answer:
                    if first_children['type'] == 'note':
                        answer= '' 
                    elif first_children['type'] == 'photo':
                        #photo = '/media/user/attachments/'+ gnr_answer[gnr_question+"/"+question]
                        photo = 'http://'+self.base_url+'/media/kobo/attachments/'+ gnr_answer[gnr_question+"/"+question]
                        answer = self.create_logo(photo)
                        # answer =''
                    else:
                        answer = gnr_answer[gnr_question+"/"+question]
                else:
                    answer = ''
                if 'label' in first_children:
                    question = first_children['label']
                row=[Paragraph(question, styBackground), answer]
                self.data.append(row)

    def parse_group(self, g_object):
        styNormal = styleSheet['Normal']
        styBackground = ParagraphStyle('background', parent=styNormal, backColor=colors.white)
        gnr_question = g_object['name']
        for first_children in g_object['children']:
            question = first_children['name']
            if gnr_question+"/"+question in self.main_answer:
                if first_children['type'] == 'note':
                    answer= '' 
                elif first_children['type'] == 'photo':
                    photo = 'http://'+self.base_url+'/media/kobo/attachments/'+self.main_answer[gnr_question+"/"+question]
                    answer = self.create_logo(photo)
                else:
                    answer = self.main_answer[gnr_question+"/"+question]
            else:
                answer = ''
            if 'label' in first_children:
                question = first_children['label']
            row=[Paragraph(question, styBackground), answer]
            self.data.append(row)

    def parse_individual_questions(self, parent_object):
        styNormal = styleSheet['Normal']
        styBackground = ParagraphStyle('background', parent=styNormal, backColor=colors.white)
        answer=self.main_answer
        for first_children in parent_object:
            if first_children['type'] == "repeat":
                self.parse_repeat(first_children)
            elif first_children['type'] == 'group':
                self.parse_group(first_children)
            else:
                question = first_children['name']

                if first_children['type'] == 'note' or question not in self.main_answer:
                    answer= Paragraph('', styBackground) 

                elif first_children['type'] == 'photo':
                    photo = 'http://'+self.base_url+'/media/kobo/attachments/'+self.main_answer[question]
                    answer = self.create_logo(photo)
                else:
                    answer = Paragraph(self.main_answer[question], styBackground)
                
                if 'label' in first_children:
                    question = first_children['label']
                row=(Paragraph(question, styBackground), answer)
                self.data.append(row)


    def print_users(self, pk, base_url):
        centered = PS(name = 'centered',
        fontSize = 14,
        leading = 16,
        alignment = 1,
        spaceAfter = 20,
        fontName = 'Helvetica-Bold')

        h1 = PS(
            name = 'Heading1',
            fontSize = 16,
            leading = 16,
            fontName = 'Helvetica-Bold',
            spaceAfter = 20,)

        h2 = PS(name = 'Heading2',
            fontSize = 14,
            leading = 14,
            fontName = 'Helvetica-Bold',
            spaceAfter = 20)
        h3 = PS(name = 'Heading3',
            fontSize = 12,
            leading = 12,
            fontName = 'Helvetica-BoldOblique',
            spaceAfter = 20,)
        
        self.base_url = base_url
        buffer = self.buffer
        doc = MyDocTemplate(buffer,
                                rightMargin=72,
                                leftMargin=72,
                                topMargin=72,
                                bottomMargin=72,
                                pagesize=self.pagesize)
 
        # Our container for 'Flowable' objects
        elements = []
        toc = TableOfContents()
        toc.levelStyles = [
            PS(fontName='Helvetica-Bold', fontSize=14, name='TOCHeading1', leftIndent=20, firstLineIndent=-20, spaceBefore=5, leading=10),
            PS(fontName='Helvetica', fontSize=12, name='TOCHeading2', leftIndent=40, firstLineIndent=-20, spaceBefore=3, leading=10),
            PS(fontName='Helvetica', ontSize=10, name='TOCHeading3', leftIndent=40, firstLineIndent=-20, spaceBefore=3, leading=10),
        ]
        elements.append(Paragraph('Responses Report for Site', centered))
        elements.append(PageBreak())
        elements.append(Paragraph('Table of contents', centered))
        elements.append(toc)
        elements.append(PageBreak())
        
        # A large collection of style sheets pre-made for us
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='centered', alignment=TA_CENTER))
        site = Site.objects.select_related('project').get(pk=pk)
        self.project_name = site.project.name
        self.project_logo = site.project.logo.url
        
        elements.append(Paragraph(site.name, h1))
        elements.append(Paragraph(site.identifier, styles['Normal']))
        if site.address:
            elements.append(Paragraph(site.address, styles['Normal']))
        if site.phone:
            elements.append(Paragraph(site.phone, styles['Normal']))
        if site.region:
            elements.append(Paragraph(site.region.name, styles['Normal']))

        elements.append(PageBreak())
        elements.append(Paragraph('Responses', h2))
        
        forms = FieldSightXF.objects.select_related('xf').filter(site_id=pk, is_survey=False).prefetch_related(Prefetch('site_form_instances', queryset=FInstance.objects.select_related('instance'))).order_by('-is_staged', 'is_scheduled')
        
        if not forms:
            elements.append(Paragraph("No Any Responses Yet.", styles['Heading5']))
        #a=FieldSightXF.objects.select_related('xf').filter(site_id=291).prefetch_related(Prefetch('site_form_instances', queryset=FInstance.objects.select_related('instance')))

       
        
        ts1 = TableStyle([
                ('ALIGN', (0,0), (-1,0), 'RIGHT'),
                ('BACKGROUND', (0,0), (-1,0), colors.white),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('GRID', (0,0), (-1,-1), 0.1, colors.lightgrey),
                    ])
        styNormal = styleSheet['Normal']
        styBackground = ParagraphStyle('background', parent=styNormal, backColor=colors.white)

        for form in forms:
            elements.append(Spacer(0,10))
            elements.append(Paragraph(form.xf.title, h3))
            elements.append(Paragraph(form.form_type() + " Form", styles['Heading4']))
            if form.stage:
                if form.stage.stage:
                    elements.append(Paragraph("Stage Id: " + str(form.stage.stage.order), styles['Heading5']))
                    elements.append(Paragraph("Sub Stage Id: " + str(form.stage.order), styles['Heading5']))    
                else:
                    elements.append(Paragraph("Stage Id: " + str(form.stage.order), styles['Heading5']))

            json_question = form.xf.json
            form_user_name = form.xf.user.username
            self.media_folder = form_user_name

            #cursor = get_instaces_for_site_individual_form(form.id)
            
            
            sub_count = 0
            if form.site_form_instances.all():
                for instance in form.site_form_instances.all():
                    if instance.form_status ==  0:
                        form_status = "Pending"
                    elif instance.form_status == 1:
                        form_status = "Rejected"
                    elif instance.form_status == 2:
                        form_status = "Flagged"
                    elif instance.form_status == 3:
                        form_status = "Approved"
                    sub_count += 1
                    elements.append(Spacer(0,10))
                    elements.append(Paragraph("Submision "+ str(sub_count), styles['Heading4']))
                    elements.append(Paragraph("Status : "+form_status, styles['Normal']))
                    elements.append(Paragraph("Submitted By:"+instance.submitted_by.username, styles['Normal']))
                    elements.append(Paragraph("Submitted Date:"+str(instance.date), styles['Normal']))
                    elements.append(Spacer(0,10))
                    self.data = []
                    self.main_answer = instance.instance.json
                    question = json.loads(json_question)
                    self.parse_individual_questions(question['children'])
                    

                    t1 = Table(self.data, colWidths=(60*mm, None))
                    t1.setStyle(ts1)
                    elements.append(t1)
                    elements.append(Spacer(0,10))

            else:
                elements.append(Paragraph("No Submisions Yet. ", styles['Heading5']))
            elements.append(PageBreak())
        #     else:
        #         elements.append(Paragraph("No Submissions Yet.", styles['Normal']))
        #         elements.append(Spacer(0,10)) 
        # else:
        #     elements.append(Paragraph("No Forms Yet.", styles['Normal']))
        #     elements.append(Spacer(0,10)) 
        


            # self.parse_individual_questions(json_question['children'])









     
        doc.multiBuild(elements, onLaterPages=self._header_footer)
 
        # Get the value of the BytesIO buffer and write it to the response.
        #pdf = buffer.getvalue()
        #buffer.close()
        #return pdf

    '''
        Usage with django
    @staff_member_required
    def print_users(request):
        # Create the HttpResponse object with the appropriate PDF headers.
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="My Users.pdf"'
     
        buffer = BytesIO()
     
        report = MyPrint(buffer, 'Letter')
        pdf = report.print_users()
     
        response.write(pdf)
        return response
    '''


# class NumberedCanvas(canvas.Canvas):
#     def __init__(self, *args, **kwargs):
#         canvas.Canvas.__init__(self, *args, **kwargs)
#         self._saved_page_states = []
 
    

#     def showPage(self):
#         self._saved_page_states.append(dict(self.__dict__))
#         self._startPage()
 

#     def save(self):
#         """add page info to each page (page x of y)"""
#         num_pages = len(self._saved_page_states)
#         print "----------------"
#         print num_pages
# #         count = 0
# #         for state in self._saved_page_states:
# #             count += 1
# #             if count==2:
# #                 self.__dict__.update(state)
# #                 self.draw_page_number(num_pages)
# #                 canvas.Canvas.showPage(self)
# #             canvas.Canvas.showPage(self)
                    
#         canvas.Canvas.save(self)
 
 
#     def draw_page_number(self, page_count):
#         # Change the position of this to wherever you want the page number to be
#         self.drawRightString(211 * mm, 15 * mm + (0.2 * inch),
#                              "Page %d of %d" % (self._pageNumber, page_count))




# if __name__ == '__main__':
#     buffer = BytesIO()
     
#     report = MyPrint(buffer, 'Letter')
#     pdf = report.print_users()
#     buffer.seek(0)
 
#     with open('arquivo.pdf', 'wb') as f:
#         f.write(buffer.read())

# def site_responses_report(data):
#     buffer = BytesIO()
     
#     report = MyPrint(buffer, 'Letter')
#     pdf = report.print_users(data)
#     buffer.seek(0)
 
#     with open('arquivo.pdf', 'wb') as f:
#         f.write(buffer.read())    


