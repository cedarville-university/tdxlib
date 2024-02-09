import tdxlib.tdx_report
import copy
import datetime
import tdxlib.tdx_integration
import tdxlib.tdx_api_exceptions
from typing import Union
from typing import BinaryIO

class TDXReportIntegration(tdxlib.tdx_integration.TDXIntegration):
    def __init__(self, filename: str = None, config=None):
        tdxlib.tdx_integration.TDXIntegration.__init__(self, filename, config)
        self.clean_cache()
    def make_report_call(self, url: str, action: str, post_body: dict = None):
        url_string = '/reports'
        if len(url) > 0:
            url_string += '/' + url
        if action == 'get':
            return self.make_get(url_string)
        if action == 'delete':
            return self.make_delete(url_string)
        if action == 'post' and post_body:
            return self.make_post(url_string, post_body)
        if action == 'put' and post_body:
            return self.make_put(url_string, post_body)
        if action == 'patch' and post_body:
            return self.make_patch(url_string, post_body)
        raise tdxlib.tdx_api_exceptions.TdxApiHTTPRequestError('No method ' + action + ' or no post information')
    def get_report_by_id(self, id: int, withData: bool, dataSortExpression: str) -> list:
        url_string = f"{id}?withData={withData}&dataSortExpression={dataSortExpression}"
        report_data = self.make_report_call(url_string, 'get')
        if report_data:
            return tdxlib.tdx_ticket.TDXReport(self, report_data)