import os
from mock import call, patch, Mock

from nose.tools import assert_raises

from ckanext.spatial.harvesters.gemini import GeminiHarvester
from ckanext.spatial.harvesters.gemini import GeminiWafHarvester
from ckanext.spatial.tests.unit.harvesters import TestMockServer


@patch('ckanext.spatial.harvesters.gemini.GeminiHarvester._save_gather_error')
def test_gemini_waf_extract_urls_report_link_errors(mock_save_gather_error):
    with open(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            '..',
            '..',
            'data',
            'sample-waf.html'
        )
    ) as f:
        gemini = GeminiWafHarvester()
        gemini.harvest_job = Mock()
        urls = gemini._extract_urls(f.read(), 'http://test.co.uk/xml')

        assert urls == [
            'http://test.co.uk/xml/AddressBase.xml',
            'http://test.co.uk/xml/SourcePoint.xml',
            'http://test.co.uk/xml/RealImagery.xml'
        ]
        assert mock_save_gather_error.call_args_list == [
            call('Ignoring link in WAF because it has "/": /xml/BoundaryLine.xml', gemini.harvest_job),
            call('Ignoring link in WAF because it has "/": /xml/SmallScale.xml', gemini.harvest_job)
        ]


@patch('ckanext.spatial.harvesters.gemini.GeminiHarvester.import_gemini_object')
@patch('ckanext.spatial.harvesters.gemini.GeminiHarvester._save_object_error')
def test_gemini_import_stage_exceptions_not_reraise_if_not_in_debug(mock_save_object_error, mock_import_gemini):
    mock_import_gemini.side_effect = Exception('Internal Server Error')

    gemini = GeminiHarvester()
    gemini.import_stage(Mock())


@patch('ckanext.spatial.harvesters.gemini.debug_exception_mode')
@patch('ckanext.spatial.harvesters.gemini.GeminiHarvester.import_gemini_object')
@patch('ckanext.spatial.harvesters.gemini.GeminiHarvester._save_object_error')
def test_gemini_import_stage_exceptions_reraise_if_in_debug(mock_save_object_error, mock_import_gemini, mock_os_getenv):
    mock_import_gemini.side_effect = Exception('Internal Server Error')

    gemini = GeminiHarvester()
    with assert_raises(Exception) as ex:
        gemini.import_stage(Mock())

    assert ex.exception.message == 'Internal Server Error'


class TestGeminiWithMockServer(TestMockServer):

    @patch('ckanext.spatial.harvesters.gemini.GeminiHarvester._save_gather_error')
    def test_gather_stage_handles_error(self, mock_save_gather_error):
        self.mock_server.RequestHandlerClass.response_status_code = 404
        mock_harvest_source_url = 'http://localhost:{}/harvest_source'.format(self.mock_server_port)

        mock_harvest_job = Mock()
        mock_harvest_job.source = Mock()
        mock_harvest_job.source.url = mock_harvest_source_url

        harvester = GeminiWafHarvester()

        harvester.gather_stage(mock_harvest_job)

        message, _ = mock_save_gather_error.call_args[0]

        assert "HTTPError(u'404 Client Error: Not Found for url: {url}',)".format(
            url=mock_harvest_source_url) in message
