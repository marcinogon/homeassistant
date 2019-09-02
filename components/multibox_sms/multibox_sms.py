# -*- coding: utf-8 -*-
import scrapy

class MultiboxSmsSpider(scrapy.Spider):
    name = 'multibox_sms'
    allowed_domains = ['orange.pl']
    start_urls = ['https://www.orange.pl/portal/map/map/corpo_message_box']

    def __init__(self, login = None, password= None, recipient=None, message=None):
        self._login = login
        self._password = password
        self._recipient = recipient
        self._message = message

    def parse(self, response):
        return scrapy.FormRequest.from_response(
		    response,
		    formnumber=1,
		    callback=self.post_login
		)

    def post_login(self, response):
        return scrapy.FormRequest.from_response(
		    response,
		    formnumber=1,
		    formdata={'login': self._login, 'password': self._password},
		    callback=self.post_password
		)

    def post_password(self, response):
        return scrapy.FormRequest.from_response(
		    response,
		    formnumber=1,
		    formdata={'/tp/core/profile/login/ProfileLoginFormHandler.value.login': self._login,
			      '/tp/core/profile/login/ProfileLoginFormHandler.value.password': self._password},
		    callback=self.new_message
		)

    def post_message_box(self, response):
        return scrapy.Request(
            'https://www.orange.pl/portal/map/map/corpo_message_box',
            callback=self.new_message
        )

    def new_message(self, response):
        next_page = response.xpath("//a[contains(@href, 'mbox_edit=new')]/@href")[0]
        if next_page is not None:
            return response.follow(next_page, callback=self.fill_message)

        return response

    def fill_message(self, response):
        return scrapy.FormRequest.from_response(
		    response,
            formname = 'sendSMS',
		    formdata = { 
                'enabled' : 'true',
		    	'/amg/ptk/map/messagebox/formhandlers/MessageFormHandler.to' : self._recipient,
			    '/amg/ptk/map/messagebox/formhandlers/MessageFormHandler.body' : self._message,
                '/amg/ptk/map/messagebox/formhandlers/MessageFormHandler.create.x' : '68',
                '/amg/ptk/map/messagebox/formhandlers/MessageFormHandler.create.y' : '12'
            },
            callback=self.logout
        )

    def logout(self, response):
        return scrapy.Request('https://www.orange.pl/ocp/gear/profile//logout')
