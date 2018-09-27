import json
import time
import datetime
from datetime import date

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
from onadata.libs.utils.image_tools import image_url
from onadata.apps.logger.models import Attachment

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
        self.additional_data=[]
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
        self.removeNullField = False

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
            project_logo = Image(self.project_logo)
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
                answer = Paragraph('', styBackground)
                isNull = True
                
            elif question_type == 'photo':
                #photo = '/media/user/attachments/'+ r_answer[r_question+"/"+question]

                size = "small"
                try:
                    result = Attachment.objects.filter(media_file=self.media_folder +'/attachments/'+ answer_dict[question_name])[0:1]
                    attachment = result[0]

                    if not attachment.mimetype.startswith('image'):
                        media_url = 'http://' + self.base_url +'/static/images/img-404.jpg'
                    
                    media_url = image_url(attachment, size)
                
                except:
                    media_url = 'http://' + self.base_url +'/static/images/img-404.jpg'

                answer = self.create_logo(media_url)
                isNull = False
                # answer =''
            elif question_type == 'audio' or question_type == 'video':
                media_link = 'http://'+self.base_url+'/attachment/medium?media_file='+ self.media_folder +'/attachments/'+ answer_dict[question_name]
                answer = Paragraph('<link href="'+media_link+'">Attachment</link>', styBackground)
                isNull = False
            else:
                answer_text=answer_dict[question_name]
                if len(answer_text) > 1200:
                    new_answer_text = answer_text[0:360]
                    answer_text = new_answer_text + ".... ( full answer followed after this table. )"
                    self.additional_data.append({question_label : answer_dict[question_name]})

                answer = Paragraph(answer_text, styBackground)
                isNull = False
        else:
            answer = Paragraph('', styBackground)
            isNull = True
        
        if self.removeNullField and isNull:
            pass
        else:
            row=[Paragraph(question_label, styBackground), answer]
            self.data.append(row)

    def parse_repeat(self, prev_groupname, r_object, nr_answer):
        
        r_question = prev_groupname + r_object['name']
        for r_answer in nr_answer:
            for first_children in r_object['children']:
                question_name = r_question+"/"+first_children['name']
                
                if first_children['type'] == 'group':
                    self.parse_group(r_question+"/",first_children, r_answer.get('question_name', {}))

                elif first_children['type'] == "repeat":
                    self.parse_repeat(r_question+"/", first_children, r_answer.get('question_name', []))

                else:
                    question_label = question_name
                    if 'label' in first_children:
                        question_label = first_children['label']
                    self.append_row(question_name, question_label, first_children['type'], r_answer)

    def parse_group(self, prev_groupname, g_object, g_answer):
       
        g_question = prev_groupname + g_object['name']
        for first_children in g_object['children']:
            question_name = g_question+"/"+first_children['name']

            if first_children['type'] == 'group':
                self.parse_group(g_question+"/",first_children, g_answer)

            elif first_children['type'] == "repeat":
                self.parse_repeat(g_question+"/", first_children, g_answer.get('question_name', []))

            else:
                question_label = question_name
                if 'label' in first_children:
                    question_label = first_children['label']
                self.append_row(question_name, question_label, first_children['type'], g_answer)

    def parse_individual_questions(self, parent_object):
       
        for first_children in parent_object:
            if first_children['type'] == "repeat":
                self.parse_repeat("", first_children, self.main_answer.get(first_children['name'], []))
            elif first_children['type'] == 'group':
                self.parse_group("", first_children, self.main_answer)
            else:
                question_name = first_children['name']
                question_label = question_name

                if 'label' in first_children:
                    question_label = first_children['label']
                
                self.append_row(question_name, question_label, first_children['type'], self.main_answer)


    def append_answers(self, json_question, instance, sub_count):
        elements = []
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
        self.additional_data=[]
        self.main_answer = instance.instance.json
        question = json.loads(json_question)

        self.parse_individual_questions(question['children'])
        

        t1 = Table(self.data, colWidths=(60*mm, None))
        t1.setStyle(self.ts1)
        elements.append(t1)
        elements.append(Spacer(0,10))

        if self.additional_data:
            elements.append(Paragraph("Full Answers", styles['Heading4']))
            for items in self.additional_data:
                for k,v in items.items():
                    elements.append(Paragraph(k + " : ", styles['Heading5']))
                    elements.append(Paragraph(v, self.paragraphstyle))
                    elements.append(Spacer(0,10))
        return elements

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
        
        forms = FieldSightXF.objects.select_related('xf').filter(is_survey=False, is_deleted=False).filter(Q(site_id=site.id, from_project=False) | Q(project_id=site.project_id)).prefetch_related(Prefetch('site_form_instances', queryset=FInstance.objects.select_related('instance')), Prefetch('project_form_instances', queryset=FInstance.objects.select_related('instance').filter(site_id=site.id))).order_by('-is_staged', 'is_scheduled')
         
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

            if not form.from_project and form.site_form_instances.all():
                for instance in form.site_form_instances.all():
                    self.append_answers(json_question, instance, sub_count)

            elif form.project_form_instances.all():
                for instance in form.project_form_instances.all():
                    self.append_answers(json_question, instance, sub_count)

            else:
                elements.append(Paragraph("No Submisions Yet. ", styles['Heading5']))
                elements.append(Spacer(0,10))
        self.doc.multiBuild(elements, onLaterPages=self._header_footer)

    def print_individual_response(self, pk, base_url, include_null_fields):
        self.base_url = base_url
        if include_null_fields == "1":
            self.removeNullField = True
        # Our container for 'Flowable' objects
        elements = []

        instance = FInstance.objects.get(instance_id=pk)
        

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='centered', alignment=TA_CENTER))
        if instance.site_fxf:
            site = instance.site
            project = site.project
            form = instance.site_fxf
        else:
            form = instance.project_fxf
            project = instance.project
        
        self.project_name = project.name
        self.project_logo = project.logo.url
        

        styNormal = styleSheet['Normal']
        styBackground = ParagraphStyle('background', parent=styNormal, backColor=colors.white)
        if instance.site:
            elements.append(Paragraph("Site Identifier : " + instance.site.identifier, self.h3))
            elements.append(Paragraph("Site Name : " + instance.site.name, self.h3))
            elements.append(Spacer(0,10))
        
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
        self.additional_data =[]
        self.main_answer = instance.instance.json
        question = json.loads(json_question)
        self.parse_individual_questions(question['children'])
        

        t1 = Table(self.data, colWidths=(60*mm, None))
        t1.setStyle(self.ts1)
        elements.append(t1)
        elements.append(Spacer(0,10))
        if self.additional_data:
            elements.append(Paragraph("Full Answers", styles['Heading4']))
            for items in self.additional_data:
                for k,v in items.items():
                    elements.append(Paragraph(k + " : ", styles['Heading5']))
                    elements.append(Paragraph(v, self.paragraphstyle))
                    elements.append(Spacer(0,10))
        self.doc.multiBuild(elements, onFirstPage=self._header_footer, onLaterPages=self._header_footer)


    def generateCustomSiteReport(self, pk, base_url, fs_ids, startdate, enddate, removeNullField):
        self.base_url = base_url
        self.removeNullField = removeNullField
        
 
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
        
        split_startdate = startdate.split('-')
        split_enddate = enddate.split('-')

        new_startdate = date(int(split_startdate[0]), int(split_startdate[1]), int(split_startdate[2]))
        end = date(int(split_enddate[0]), int(split_enddate[1]), int(split_enddate[2]))

        new_enddate = end + datetime.timedelta(days=1)

        forms = FieldSightXF.objects.select_related('xf').filter(pk__in=fs_ids, is_survey=False, is_deleted=False).prefetch_related(Prefetch('site_form_instances', queryset=FInstance.objects.select_related('instance').filter(date__range=[new_startdate, new_enddate])), Prefetch('project_form_instances', queryset=FInstance.objects.select_related('instance').filter(site_id=site.id, date__range=[new_startdate, new_enddate]))).order_by('-is_staged', 'is_scheduled')
        
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
            if not form.from_project and form.site_form_instances.all():
                for instance in form.site_form_instances.all():
                    new_elements = self.append_answers(json_question, instance, sub_count)
                    elements+=new_elements
                    
            elif form.project_form_instances.all():
                for instance in form.project_form_instances.all():
                    new_elements = self.append_answers(json_question, instance, sub_count)
                    elements+=new_elements

            else:
                elements.append(Paragraph("No Submisions Yet. ", styles['Heading5']))
                elements.append(Spacer(0,10))
        self.doc.multiBuild(elements, onLaterPages=self._header_footer)