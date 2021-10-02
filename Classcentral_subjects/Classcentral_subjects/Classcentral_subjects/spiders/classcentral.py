import scrapy
from scrapy.http import Request
import logging

class ClasscentralSpider(scrapy.Spider):
    name = 'classcentral'
    allowed_domains = ['classcentral.com']
    start_urls = ['https://www.classcentral.com/subjects']

    def __init__(self, subject=None):
        self.subject = subject

    def parse(self, response):
        if self.subject:
            subject_url = response.xpath("//a[contains(@title, '"+ self.subject +"')]/@href").get()
            absolute_subject_url = response.urljoin(subject_url)
            yield Request(absolute_subject_url, callback=self.parse_course)
        else:
            logging.info('Scraping all subjects.')
            subject_links = response.xpath("//h3[@class='row vert-align-middle']")
            for subject in subject_links:
                subject_url = subject.xpath(".//a[contains(@href, 'subject')]/@href").get()
                absolute_subject_url = response.urljoin(subject_url)
                yield Request(absolute_subject_url, callback=self.parse_course)

    def parse_course(self, response):
        subject_name = response.xpath("//h1/text()").get()

        courses_name = response.xpath("//li[@itemtype='http://schema.org/Event']")
        for course in courses_name:
            course_name = course.xpath(".//h2[@itemprop='name']/text()").get()
            course_url = course.xpath(".//a[contains(@href, '/course/')]/@href").get()
            absolute_course_url = response.urljoin(course_url)

            yield{'subject_name': subject_name,
                  'course_name': course_name,
                  'absolute_course_url': absolute_course_url}

        next_page_url = response.xpath("//link[@rel='next']/@href").get()
        if next_page_url is not None:
            absolute_next_page_url = response.urljoin(next_page_url)
            yield Request(absolute_next_page_url, callback=self.parse_course)

