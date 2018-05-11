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
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
styleSheet = getSampleStyleSheet()
styles = getSampleStyleSheet()

class MyDocTemplate(SimpleDocTemplate):
     def __init__(self, filename, **kw):
         self.allowSplitting = 1
         apply(SimpleDocTemplate.__init__, (self, filename), kw)
         pdfmetrics.registerFont(TTFont('arialuni', 'ARIALUNI.TTF'))

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

class PDFReport:


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

        self.centered = PS(name = 'centered',
        fontSize = 14,
        leading = 16,
        alignment = 1,
        spaceAfter = 20,
        fontName = 'arialuni')
        

        self.bodystyle = PS(
            name = 'bodystyle',
            parent=styles['Normal'],
            fontSize = 8,
            fontName = 'arialuni',
            )

        self.paragraphstyle = PS(
            name = 'paragraphstyle',
            parent=styles['Normal'],
            fontSize = 9,
            fontName = 'arialuni',
            )

        self.h1 = PS(
            name = 'Heading1',
            fontSize = 16,
            leading = 16,
            fontName = 'arialuni',
            spaceAfter = 20,)

        self.h2 = PS(name = 'Heading2',
            fontSize = 14,
            leading = 14,
            fontName = 'arialuni',
            spaceAfter = 20)
        self.h3 = PS(name = 'Heading3',
            fontSize = 12,
            leading = 12,
            fontName = 'arialuni',
            spaceAfter = 20,)
        self.ts1 = TableStyle([
                ('ALIGN', (0,0), (-1,0), 'RIGHT'),
                ('BACKGROUND', (0,0), (-1,0), colors.white),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('GRID', (0,0), (-1,-1), 0.1, colors.lightgrey),
                    ])
        buffer = self.buffer
        self.doc = MyDocTemplate(buffer,
                                rightMargin=72,
                                leftMargin=72,
                                topMargin=72,
                                bottomMargin=72,
                                pagesize=self.pagesize)


    def create_logo(self, absolute_path):
        try:
            image = Image(absolute_path)
            image._restrictSize(2.5 * inch, 2.5 * inch)
        except:
            image = Image('http://' + self.base_url +'/static/images/img-404.jpg')
            image._restrictSize(1.5 * inch, 1.5 * inch)
        return image

    def _header_footer(self, canvas, doc):
        # Save the state of our canvas so we can draw on it
        canvas.saveState()
        
        style_right = ParagraphStyle(name='right', parent=self.bodystyle, fontName='arialuni',
                fontSize=10, alignment=TA_RIGHT)
        
        fieldsight_logo = Image('http://' + self.base_url +'/static/images/fs1.jpg')
        fieldsight_logo._restrictSize(1.5 * inch, 1.5 * inch)
        

        # headerleft = Paragraph("FieldSight", self.bodystyle)
        headerright = Paragraph(self.project_name, style_right)

        # w1, h1 = headerleft.wrap(doc.width, doc.topMargin)
        w2, h2 = headerright.wrap(doc.width, doc.topMargin)

        textWidth = stringWidth(self.project_name, fontName='arialuni',
                fontSize=10) 
        
        fieldsight_logo.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin + 12)
        headerright.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin + 20)
        try:
            project_logo = Image('http://' + self.base_url + self.project_logo)
            project_logo._restrictSize(0.4 * inch, 0.4 * inch)
            project_logo.drawOn(canvas, headerright.width + doc.leftMargin -0.5 * inch - textWidth, doc.height + doc.topMargin + 10)
        except:
            pass        
        # header.drawOn(canvas, doc.leftMargin + doc.width, doc.height + doc.topMargin +20)
        
        # Footer
        footer = Paragraph('Page no. '+str(canvas._pageNumber), style_right)
        w, h = footer.wrap(doc.width, doc.bottomMargin)
        footer.drawOn(canvas, doc.leftMargin, h + 40)
 
        # Release the canvas
        canvas.restoreState()
    
    def append_row(self, question_name, question_label, question_type, answer_dict):
        styNormal = self.bodystyle
        styBackground = ParagraphStyle('background', parent=styNormal, backColor=colors.white)
        if question_name in answer_dict:
            if question_type == 'note':
                answer=Paragraph('', styBackground)
                
            elif question_type == 'photo':
                #photo = '/media/user/attachments/'+ r_answer[r_question+"/"+question]
                photo = 'http://'+self.base_url+'/media/'+ self.media_folder +'/attachments/'+ answer_dict[question_name]
                answer = self.create_logo(photo)
                # answer =''
            elif question_type == 'audio' or question_type == 'video':
                media_link = 'http://'+self.base_url+'/media/'+ self.media_folder +'/attachments/'+ answer_dict[question_name]
                answer = Paragraph('<link href="'+media_link+'">Attachment</link>', styBackground)

            else:
                answer_text=answer_dict[question_name]
                if len(answer_text) > 1200:
                    new_answer_text = answer[0:360]
                    answer_text = new_answer_text + ".... ( full answer at end of submission table. )"

                answer = Paragraph(answer_text, styBackground)
        else:
            answer=Paragraph('', styBackground)
        
        row=[Paragraph(question_label, styBackground), answer]
        self.data.append(row)

    def parse_repeat(self, r_object):
        
        r_question = r_object['name']
        for r_answer in self.main_answer[r_question]:
            for first_children in r_object['children']:
                question_name = r_question+"/"+first_children['name']
                question_label = question_name
                
                if 'label' in first_children:
                    question_label = first_children['label']

                self.append_row(question_name, question_label, first_children['type'], r_answer)

    def parse_group(self, prev_groupname, g_object):
       
        g_question = prev_groupname+g_object['name']
        for first_children in g_object['children']:
            question_name = g_question+"/"+first_children['name']
            question_label = question_name

            if 'label' in first_children:
                question_label = first_children['label']
            
            self.append_row(question_name, question_label, first_children['type'], self.main_answer)
            
            # done at the end because wee want to print group name as well in report.
            if first_children['type'] == 'group':
                self.parse_group(g_question+"/",first_children)

    def parse_individual_questions(self, parent_object):
       
        for first_children in parent_object:
            if first_children['type'] == "repeat":
                self.parse_repeat(first_children)
            elif first_children['type'] == 'group':
                self.parse_group("", first_children)
            else:
                question_name = first_children['name']
                question_label = question_name

                if 'label' in first_children:
                    question_label = first_children['label']
                
                self.append_row(question_name, question_label, first_children['type'], self.main_answer)



    def generateFullReport(self, pk, base_url):
        self.base_url = base_url
        
 
        # Our container for 'Flowable' objects
        elements = []
        toc = TableOfContents()
        toc.levelStyles = [
            PS(fontName='arialuni', fontSize=12, name='TOCHeading1', leftIndent=20, firstLineIndent=-20, spaceBefore=5, leading=10),
            PS(fontName='arialuni', fontSize=10, name='TOCHeading2', leftIndent=40, firstLineIndent=-20, spaceBefore=3, leading=10),
            PS(fontName='arialuni', fontSize=9, name='TOCHeading3', leftIndent=40, firstLineIndent=-20, spaceBefore=3, leading=10),
        ]
        elements.append(Paragraph('Responses Report for Site', self.centered))
        elements.append(PageBreak())
        elements.append(Paragraph('Table of contents', self.centered))
        elements.append(toc)
        elements.append(PageBreak())
        
        # A large collection of style sheets pre-made for us
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='centered', alignment=TA_CENTER))
        site = Site.objects.select_related('project').get(pk=pk)
        self.project_name = site.project.name
        self.project_logo = site.project.logo.url
        
        elements.append(Paragraph(site.name, self.h1))
        elements.append(Paragraph(site.identifier, styles['Normal']))
        if site.address:
            elements.append(Paragraph(site.address, styles['Normal']))
        if site.phone:
            elements.append(Paragraph(site.phone, styles['Normal']))
        if site.region:
            elements.append(Paragraph(site.region.name, styles['Normal']))

        elements.append(PageBreak())
        elements.append(Paragraph('Responses', self.h2))
        
        forms = FieldSightXF.objects.select_related('xf').filter(site_id=pk, is_survey=False, is_deleted=False).prefetch_related(Prefetch('site_form_instances', queryset=FInstance.objects.select_related('instance'))).order_by('-is_staged', 'is_scheduled')
        
        if not forms:
            elements.append(Paragraph("No Any Responses Yet.", styles['Heading5']))
        #a=FieldSightXF.objects.select_related('xf').filter(site_id=291).prefetch_related(Prefetch('site_form_instances', queryset=FInstance.objects.select_related('instance')))

       
        styNormal = styleSheet['Normal']
        styBackground = ParagraphStyle('background', parent=styNormal, backColor=colors.white)

        for form in forms:
            elements.append(Spacer(0,10))
            elements.append(Paragraph(form.xf.title, self.h3))
            elements.append(Paragraph(form.form_type() + " Form", styles['Heading4']))
            if form.stage:
                if form.stage.stage:
                    elements.append(Paragraph("Stage Id: " + str(form.stage.stage.order), self.paragraphstyle))
                    elements.append(Paragraph("Sub Stage Id: " + str(form.stage.order), self.paragraphstyle))    
                else:
                    elements.append(Paragraph("Stage Id: " + str(form.stage.order), self.paragraphstyle))

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
                    elements.append(Paragraph("Submision "+ str(sub_count), self.paragraphstyle))
                    elements.append(Paragraph("Status : "+form_status, self.paragraphstyle))
                    elements.append(Paragraph("Submitted By:"+instance.submitted_by.username, self.paragraphstyle))
                    elements.append(Paragraph("Submitted Date:"+str(instance.date), self.paragraphstyle))
                    elements.append(Spacer(0,10))
                    self.data = []
                    self.main_answer = instance.instance.json
                    question = json.loads(json_question)
                    self.parse_individual_questions(question['children'])
                    

                    t1 = Table(self.data, colWidths=(60*mm, None))
                    t1.setStyle(self.ts1)
                    elements.append(t1)
                    elements.append(Spacer(0,10))

            else:
                elements.append(Paragraph("No Submisions Yet. ", styles['Heading5']))
                elements.append(Spacer(0,10))
        self.doc.multiBuild(elements, onLaterPages=self._header_footer)

    def print_individual_response(self, pk, base_url):
        self.base_url = base_url
 
        # Our container for 'Flowable' objects
        elements = []

        instance = FInstance.objects.get(instance_id=pk)
        form = instance.site_fxf

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='centered', alignment=TA_CENTER))
        site = instance.site
        self.project_name = site.project.name
        self.project_logo = site.project.logo.url
        

        
        styNormal = styleSheet['Normal']
        styBackground = ParagraphStyle('background', parent=styNormal, backColor=colors.white)

        elements.append(Paragraph(form.xf.title, self.h3))
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
            
            
        if instance.form_status ==  0:
            form_status = "Pending"
        elif instance.form_status == 1:
            form_status = "Rejected"
        elif instance.form_status == 2:
            form_status = "Flagged"
        elif instance.form_status == 3:
            form_status = "Approved"

        elements.append(Spacer(0,10))
        elements.append(Paragraph("Status : "+form_status, styles['Normal']))
        elements.append(Paragraph("Submitted By:"+instance.submitted_by.username, styles['Normal']))
        elements.append(Paragraph("Submitted Date:"+str(instance.date), styles['Normal']))
        elements.append(Spacer(0,10))
        self.data = []
        self.main_answer = instance.instance.json
        question = json.loads(json_question)
        self.parse_individual_questions(question['children'])
        

        t1 = Table(self.data, colWidths=(60*mm, None))
        t1.setStyle(self.ts1)
        elements.append(t1)
        elements.append(Spacer(0,10))
        self.doc.multiBuild(elements, onFirstPage=self._header_footer, onLaterPages=self._header_footer)


    def generateCustomSiteReport(self, pk, base_url, fs_ids, startdate, enddate):
        self.base_url = base_url
        
 
        # Our container for 'Flowable' objects
        elements = []
        toc = TableOfContents()
        toc.levelStyles = [
            PS(fontName='arialuni', fontSize=12, name='TOCHeading1', leftIndent=20, firstLineIndent=-20, spaceBefore=5, leading=10),
            PS(fontName='arialuni', fontSize=10, name='TOCHeading2', leftIndent=40, firstLineIndent=-20, spaceBefore=3, leading=10),
            PS(fontName='arialuni', fontSize=9, name='TOCHeading3', leftIndent=40, firstLineIndent=-20, spaceBefore=3, leading=10),
        ]
        elements.append(Paragraph('Custom Responses Report for Site', self.centered))
        elements.append(PageBreak())
        elements.append(Paragraph('Table of contents', self.centered))
        elements.append(toc)
        elements.append(PageBreak())
        
        # A large collection of style sheets pre-made for us
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='centered', alignment=TA_CENTER))
        site = Site.objects.select_related('project').get(pk=pk)
        self.project_name = site.project.name
        self.project_logo = site.project.logo.url
        
        elements.append(Paragraph(site.name, self.h1))
        elements.append(Paragraph(site.identifier, styles['Normal']))
        if site.address:
            elements.append(Paragraph(site.address, styles['Normal']))
        if site.phone:
            elements.append(Paragraph(site.phone, styles['Normal']))
        if site.region:
            elements.append(Paragraph(site.region.name, styles['Normal']))

        elements.append(PageBreak())
        elements.append(Paragraph('Responses', self.h2))
        
        forms = FieldSightXF.objects.select_related('xf').filter(pk__in=fs_ids, is_survey=False, is_deleted=False).prefetch_related(Prefetch('site_form_instances', queryset=FInstance.objects.select_related('instance').filter(date__range=[startdate, enddate]))).order_by('-is_staged', 'is_scheduled')
        
        if not forms:
            elements.append(Paragraph("No Any Responses Yet.", styles['Heading5']))
        #a=FieldSightXF.objects.select_related('xf').filter(site_id=291).prefetch_related(Prefetch('site_form_instances', queryset=FInstance.objects.select_related('instance')))

       
        
       
        styNormal = styleSheet['Normal']
        styBackground = ParagraphStyle('background', parent=styNormal, backColor=colors.white)

        for form in forms:
            elements.append(Spacer(0,10))
            elements.append(Paragraph(form.xf.title, self.h3))
            elements.append(Paragraph(form.form_type() + " Form", styles['Heading4']))
            if form.stage:
                if form.stage.stage:
                    elements.append(Paragraph("Stage Id: " + str(form.stage.stage.order), self.paragraphstyle))
                    elements.append(Paragraph("Sub Stage Id: " + str(form.stage.order), self.paragraphstyle))    
                else:
                    elements.append(Paragraph("Stage Id: " + str(form.stage.order), self.paragraphstyle))

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
                    elements.append(Paragraph("Submision "+ str(sub_count), self.paragraphstyle))
                    elements.append(Paragraph("Status : "+form_status, self.paragraphstyle))
                    elements.append(Paragraph("Submitted By:"+instance.submitted_by.username, self.paragraphstyle))
                    elements.append(Paragraph("Submitted Date:"+str(instance.date), self.paragraphstyle))
                    elements.append(Spacer(0,10))
                    self.data = []
                    self.main_answer = instance.instance.json
                    question = json.loads(json_question)
                    self.parse_individual_questions(question['children'])
                    

                    t1 = Table(self.data, colWidths=(60*mm, None))
                    t1.setStyle(self.ts1)
                    elements.append(t1)
                    elements.append(Spacer(0,10))

            else:
                elements.append(Paragraph("No Submisions Yet. ", styles['Heading5']))
                elements.append(Spacer(0,10))
        self.doc.multiBuild(elements, onLaterPages=self._header_footer)