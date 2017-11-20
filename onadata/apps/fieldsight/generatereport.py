import json
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.platypus import Spacer, SimpleDocTemplate, Table, TableStyle
from reportlab.platypus import Image
from reportlab.lib import colors
from onadata.apps.fsforms.reports_util import get_instaces_for_site_individual_form

styleSheet = getSampleStyleSheet()
 
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
    @staticmethod
    def _header_footer(canvas, doc):
        # Save the state of our canvas so we can draw on it
        canvas.saveState()
        styles = getSampleStyleSheet()
 
        # Header
        header = Paragraph('Fieldsight   ' * 5, styles['Normal'])
        w, h = header.wrap(doc.width, doc.topMargin)
        header.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin)
 
        # Footer
        footer = Paragraph('Naxalicious  ' * 5, styles['Normal'])
        w, h = footer.wrap(doc.width, doc.bottomMargin)
        footer.drawOn(canvas, doc.leftMargin, h)
 
        # Release the canvas
        canvas.restoreState()
    def create_logo(self, absolute_path):
        image = Image(absolute_path)
        image._restrictSize(3 * inch, 3 * inch) 
        return image
    def parse_repeat(self, r_object):
        styNormal = styleSheet['Normal']
        styBackground = ParagraphStyle('background', parent=styNormal, backColor=colors.pink)
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
                        photo = 'http://'+self.base_url+'/media/'+media_folder+'/attachments/'+ gnr_answer[gnr_question+"/"+question]
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
        styBackground = ParagraphStyle('background', parent=styNormal, backColor=colors.pink)
        gnr_question = g_object['name']
        for first_children in g_object['children']:
            question = first_children['name']
            if gnr_question+"/"+question in self.main_answer:
                if first_children['type'] == 'note':
                    answer= '' 
                elif first_children['type'] == 'photo':
                    photo = 'http://'+self.base_url+'/media/'+media_folder+'/attachments/'+self.main_answer[gnr_question+"/"+question]
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
        styBackground = ParagraphStyle('background', parent=styNormal, backColor=colors.pink)
        answer=self.main_answer
        for first_children in parent_object:
            if first_children['type'] == "repeat":
                self.parse_repeat(first_children)
            elif first_children['type'] == 'group':
                self.parse_group(first_children)
            else:
                question = first_children['name']
                if 'label' in first_children:
                    question = first_children['label']

                if first_children['type'] == 'note' or question not in self.main_answer:
                    answer= '' 

                elif first_children['type'] == 'photo':
                    photo = 'http://'+self.base_url+'/media/'+media_folder+'/attachments/'+self.main_answer[question]
                    answer = self.create_logo(photo)
                else:
                    answer = self.main_answer[question]
                
                row=(Paragraph(question, styBackground), Paragraph(answer, styBackground))
                self.data.append(row)


    def print_users(self, forms, base_url):
        self.base_url = base_url
        buffer = self.buffer
        doc = SimpleDocTemplate(buffer,
                                rightMargin=72,
                                leftMargin=72,
                                topMargin=72,
                                bottomMargin=72,
                                pagesize=self.pagesize)
 
        # Our container for 'Flowable' objects
        elements = []
        
        # A large collection of style sheets pre-made for us
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='centered', alignment=TA_CENTER))
        elements.append(Paragraph('Site Resonses', styles['Heading1']))


       
        

        # print q

        # for qq in q['children']:
        #     print ""
        #     print ""
        #     print qq

        
        # print json.dumps(self.data)
        # print q['start']


        # Draw things on the PDF. Here's where the PDF generation happens.
        # See the ReportLab documentation for the full list of functionality.
        # users = [
           
        # ]
        # # elements.append(Paragraph('My User Names', styles['Heading1']))
        # # print data
        # # for i, user in enumerate(users):
        # #         elements.append(Paragraph(user['name'], styles['Normal']))
       

        for form in forms:
            elements.append(Paragraph("Form Name:"+form.xf.title, styles['Normal']))
            json_question = form.xf.json
            form_user_name = form.xf.user.username
            self.media_folder = form_user_name
            elements.append(Paragraph("Form Created By:"+form_user_name, styles['Normal']))
            cursor = get_instaces_for_site_individual_form(form.id)
            styNormal = styleSheet['Normal']
            styBackground = ParagraphStyle('background', parent=styNormal, backColor=colors.pink)
            ts1 = TableStyle([
                ('ALIGN', (0,0), (-1,0), 'RIGHT'),
                ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('GRID', (0,0), (-1,-1), 0.25, colors.black),
                    ])
            for instance in cursor:
              t1 = None
              self.main_answer = instance
              question = json.loads(json_question)
              self.parse_individual_questions(question['children'])
              

              t1 = Table(self.data, colWidths=(60*mm, None))
              t1.setStyle(ts1)
              elements.append(Spacer(0,10))
              elements.append(t1)
              elements.append(Paragraph("===============", styles['Normal']))
              elements.append(Spacer(0,10))
        #     else:
        #         elements.append(Paragraph("No Submissions Yet.", styles['Normal']))
        #         elements.append(Spacer(0,10)) 
        # else:
        #     elements.append(Paragraph("No Forms Yet.", styles['Normal']))
        #     elements.append(Spacer(0,10)) 
        


            # self.parse_individual_questions(json_question['children'])









     
        doc.build(elements, onFirstPage=self._header_footer, onLaterPages=self._header_footer,
                  canvasmaker=NumberedCanvas)
 
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


class NumberedCanvas(canvas.Canvas):


    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []
 

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()
 

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)
 
 
    def draw_page_number(self, page_count):
        # Change the position of this to wherever you want the page number to be
        self.drawRightString(211 * mm, 15 * mm + (0.2 * inch),
                             "Page %d of %d" % (self._pageNumber, page_count))




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
