import tdxlib.tdx_report
import copy
import datetime
from tdxlib.tdx_integration import TDXIntegration
import tdxlib.tdx_api_exceptions
from typing import Union
from typing import BinaryIO
import json

class TDXReportIntegration(TDXIntegration):
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
    def get_report_by_id(self, id: int, withData: bool = False, dataSortExpression: str = "") -> tdxlib.tdx_report.TDXReport:
        url_string = f"{id}?withData={withData}&dataSortExpression={dataSortExpression}"
        report_data = self.make_report_call(url_string, 'get')
        if report_data:
            #return tdxlib.tdx_report.TDXReport.__init__(integration=self, json=report_data)
            result: tdxlib.tdx_report.TDXReport = {
                'report_data': report_data,
                'tdx_api': self
            }
            return result