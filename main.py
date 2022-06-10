import os
import smtplib
from email.message import EmailMessage
from email.headerregistry import Address
from email.utils import make_msgid
from jinja2 import Template
import imghdr


class Message:
    def __init__(self, subject:str, from_: Address, to:Address):
        self.msg = EmailMessage()
        self.msg['subject'] = subject
        self.msg['from'] = from_
        self.msg['To'] = to


    def add_plain_text(self, file:str):
        """add the plain text to the message from txt file"""
        with open(file) as f:
            self.msg.set_content(f.read())


    def add_html(self, html:str, template_images:list[str] = None, template_vars:dict = None):
        """add the html part to the message"""
        img_dict = {}
        # add modified file name as a key and cid as a value to the dictionary
        # the modification is that the dots are replaced with underscores in the file names
        if template_images:
            for image in template_images:
                template_var = os.path.basename(image).replace('.', '_')
                img_dict[template_var] = make_msgid()[1:-1]

        # reads html and creates jinja's template
        with open(html) as f:
            t = Template(f.read())

        # adds html to the message
        if template_vars:
            self.msg.add_alternative(t.render(**img_dict, **template_vars), subtype='html')
        else:
            self.msg.add_alternative(t.render(**img_dict), subtype='html')

        if template_images:
        # adds images to html
            for image in template_images:
                with open(image, 'rb') as img:
                    img_data = img.read()
                    template_filename = os.path.basename(image).replace('.', '_')
                    ind = len(self.msg.get_payload())-1
                    self.msg.get_payload()[ind].add_related(img_data, 'image', imghdr.what(None, img_data),
                                                          cid=img_dict[template_filename], filename=image)


    def attach_images(self, img_list: list[str]):
        """add the html part to the message"""
        for file in img_list:
            with open(file, 'rb') as f:
                img_data = f.read()
            self.msg.add_attachment(img_data, maintype='image', subtype=imghdr.what(None, img_data), filename=file)


    def attach_app_files(self, app_files: list[str]):
        """attach files with internal format of the application programm: pdf, docx, xlsx, etc. from files list"""
        for file in app_files:
            with open(file, 'rb') as attached_file:
                attached_file_data = attached_file.read()
            self.msg.add_attachment(attached_file_data, maintype='application', subtype='octet-stream', filename=file)


    def send(self, smpt_host:str, port:int, login:str, password:str,):
        smtp_obj = smtplib.SMTP_SSL(smpt_host, port)
        smtp_obj.ehlo()
        smtp_obj.login(login, password)
        smtp_obj.send_message(self.msg)
        smtp_obj.quit()


if __name__ == "__main__":
    SMTP_HOST = 'smpt.mail.ru'
    PORT = 465
    LOGIN = 'login'
    PASSWORD = 'password'
    SUBJECT = 'subject'
    FROM = Address("display_name", "username", "domain")
    DISTRIBUTION_LIST = [Address("display_name", "username", "domain"),
                         ]
    for TO in DISTRIBUTION_LIST:
        message = Message(SUBJECT, FROM, TO)
        message.add_plain_text('./test.txt')
        message.add_html('./test.html', template_images=['./test.webp', './logo.png'],
                         template_vars=dict(a=[1, 2, 3, 4]))
        message.attach_images(['./logo.png', './test.webp'])
        message.attach_app_files(['./test.pdf', './test.docx', './test.xlsx'])
        message.send(SMTP_HOST, PORT, LOGIN, PASSWORD)
        print(f"{TO} - has been sent")


