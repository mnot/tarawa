
from common import PipelineComponent

class ContentCode(PipelineComponent):
    def send_request(self, request, response):
        request.headers['Accept-Encoding']
    def receive_request(self, request, response):
        if request.headers['Accept-Encoding']
    def send_response(self, request, response):
        response.headers['Content-Encoding']
    def receive_response(self, request, response):
        if response.headers['Content-Encoding']
        