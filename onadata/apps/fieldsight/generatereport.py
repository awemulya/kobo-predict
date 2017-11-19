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

styleSheet = getSampleStyleSheet()
 
class MyPrint:


    def __init__(self, buffer, pagesize):
        self.answer = {u'__version__': u'3675', u'_geolocation': [27.88883562, 85.77280079],
         u'_submission_time': u'2017-11-12T09:07:31',
         u'_submitted_by': u'sulax2017',
         u'_xform_id_string': u'aaL5F2CHSiNVogLbyb54yK',
         u'end': u'2017-11-12T14:50:36.402+05:45',
         u'formhub/uuid': u'c94a9da48d4748d4bdc815f4a05ace0f',
         u'group_md5fu05': [{u'group_md5fu05/brief_explanation_of_photograph': u'Crown part of the landslide',
           u'group_md5fu05/photograph': u'1510137163267.jpg'},
          {u'group_md5fu05/brief_explanation_of_photograph': u'Downslope view of from the settlement',
           u'group_md5fu05/photograph': u'1510137183753.jpg'},
          {u'group_md5fu05/brief_explanation_of_photograph': u'Settlement',
           u'group_md5fu05/photograph': u'1510137231088.jpg'},
          {u'group_md5fu05/brief_explanation_of_photograph': u'Downslope view from landslide',
           u'group_md5fu05/photograph': u'1510137319805.jpg'},
          {u'group_md5fu05/photograph': u'1510138045834.jpg'},
          {u'group_md5fu05/brief_explanation_of_photograph': u'Shear zone seen along the road',
           u'group_md5fu05/photograph': u'1510138153572.jpg'},
          {u'group_md5fu05/photograph': u'1510138171216.jpg'},
          {u'group_md5fu05/brief_explanation_of_photograph': u'Close up view',
           u'group_md5fu05/photograph': u'1510138205633.jpg'},
          {u'group_md5fu05/photograph': u'1510138244944.jpg'},
          {u'group_md5fu05/photograph': u'1510138319607.jpg'},
          {u'group_md5fu05/brief_explanation_of_photograph': u'Rock outcrop and zoints',
           u'group_md5fu05/photograph': u'1510150248447.jpg'},
          {u'group_md5fu05/photograph': u'1510150291827.jpg'}],
         u'meta/instanceID': u'uuid:83cd98ad-ea41-4f8f-af1e-5006ea978e15',
         u'settlement_location': u'27.88883562 85.77280079 1539.0 5.0',
         u'settlement_name': u'Ghunga, kartikay',
         u'settlement_reference_number': u'Si038',
         u'start': u'2017-11-08T16:16:28.146+05:45'}
        self.data=[]
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        elif pagesize == 'Letter':
            self.pagesize = letter
        self.width, self.height = self.pagesize
        self.base_url = ''
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
    def parse_group_n_repeat(self, gnr_object):
        styNormal = styleSheet['Normal']
        styBackground = ParagraphStyle('background', parent=styNormal, backColor=colors.pink)
        gnr_question = gnr_object['name']
        for gnr_answer in self.answer[gnr_question]:
            for first_children in gnr_object['children']:
                question = first_children['name']
                group_answer = self.answer[gnr_question]
                question_label = first_children['label']
                if gnr_question+"/"+question in gnr_answer:
                    if first_children['type'] == 'note':
                        answer= '' 
                    elif first_children['type'] == 'photo':
                        #photo = '/media/user/attachments/'+ gnr_answer[gnr_question+"/"+question]
                        #photo = 'http://'+self.base_url+'/media/user_aasis/Screenshot%20from%202017-08-02%2012-45-05.png'
                        #answer = self.create_logo(photo)
                        answer =''
                    else:
                        answer = gnr_answer[gnr_question+"/"+question]
                else:
                    answer = ''
                if 'label' in first_children:
                    question = first_children['label']
                row=[Paragraph(question, styBackground), answer]
                self.data.append(row)

    def parse_individual_questions(self, parent_object):
        styNormal = styleSheet['Normal']
        styBackground = ParagraphStyle('background', parent=styNormal, backColor=colors.pink)
        for first_children in parent_object:
            if first_children['type'] == 'group' or first_children['type'] == "repeat":
                if not first_children['name'] == 'meta':
                    self.parse_group_n_repeat(first_children)
            else:
                question = first_children['name']
                if first_children['type'] == 'note':
                    answer= '' 

                elif first_children['type'] == 'photo':
                    answer = '/media/user/attachments/'+self.answer[question]
                else:
                    answer = self.answer[question]
                if 'label' in first_children:
                    question = first_children['label']
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


        q={u'children': [{u'bind': {u'required': u'true'},
   u'label': u'Settlement Reference Number',
   u'name': u'settlement_reference_number',
   u'type': u'text'},
  {u'bind': {u'required': u'true'},
   u'label': u'Settlement Name',
   u'name': u'settlement_name',
   u'type': u'text'},
  {u'bind': {u'required': u'false'},
   u'label': u'Settlement Location',
   u'name': u'settlement_location',
   u'type': u'geopoint'},
  {u'bind': {u'required': u'false'},
   u'label': u'Please take and upload additional photographs using this form. For each photograph, you will be asked to upload a photograph and a brief explanation. You can add additional photographs by adding a "group."',
   u'name': u'please_take_and_upload_additional_photographs_using_this_form_for_each_photograph_you_will_be_asked_to_upload_a_photograph_and_a_brief_explanation_you_can_add_additional_photographs_by_adding_a_group_',
   u'type': u'note'},
  {u'children': [{u'bind': {u'required': u'false'},
     u'label': u'Photograph',
     u'name': u'photograph',
     u'type': u'photo'},
    {u'bind': {u'required': u'false'},
     u'label': u'Brief Explanation of Photograph',
     u'name': u'brief_explanation_of_photograph',
     u'type': u'text'}],
   u'control': {u'appearance': u'field-list'},
   u'label': u'Photograph',
   u'name': u'group_md5fu05',
   u'type': u'repeat'},
  {u'name': u'start', u'type': u'start'},
  {u'name': u'end', u'type': u'end'},
  {u'bind': {u'calculate': u'3675'},
   u'name': u'__version__',
   u'type': u'calculate'},
  {u'children': [{u'bind': {u'calculate': u"concat('uuid:', uuid())",
      u'readonly': u'true()'},
     u'name': u'instanceID',
     u'type': u'calculate'}],
   u'control': {u'bodyless': True},
   u'name': u'meta',
   u'type': u'group'}],
 u'default_language': u'default',
 u'id_string': u'aaL5F2CHSiNVogLbyb54yK',
 u'name': u'aaL5F2CHSiNVogLbyb54yK',
 u'sms_keyword': u'aaL5F2CHSiNVogLbyb54yK',
 u'title': u'Form 8 Photographs',
 u'type': u'survey',
 u'version': u'3675'}

        

        # print q

        # for qq in q['children']:
        #     print ""
        #     print ""
        #     print qq

        self.parse_individual_questions(q['children'])
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
        styNormal = styleSheet['Normal']
        styBackground = ParagraphStyle('background', parent=styNormal, backColor=colors.pink)
        ts1 = TableStyle([
            ('ALIGN', (0,0), (-1,0), 'RIGHT'),
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('GRID', (0,0), (-1,-1), 0.25, colors.black),
                ])

        t1 = Table(self.data, colWidths=(60*mm, None))
        t1.setStyle(ts1)
        elements.append(t1)

        for form in forms:
            elements.append(Paragraph(form.xf.title, styles['Normal']))
            json_question = form.xf.json
            form_user_name = form.xf.user
            elements.append(Paragraph(form_user_name, styles['Normal']))
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
