import requests

from mock import patch, Mock

from nose.tools import assert_raises

from ckanext.spatial.harvesters.base import SpatialHarvester

from ckanext.spatial.tests.unit.harvesters import TestMockServer


class TestBaseWithMockServer(TestMockServer):

    def test_get_content_as_unicode_raises_error_for_status(self):
        self.mock_server.RequestHandlerClass.response_status_code = requests.codes.NOT_FOUND
        self.mock_server.RequestHandlerClass.response_content = (
            "<?xml version='1.0' encoding='ASCII'?><test>test content</test>"
        )

        mock_harvest_source_url = 'http://localhost:{}/harvest_source'.format(self.mock_server_port)

        harvester = SpatialHarvester()
        with assert_raises(requests.HTTPError) as ex:
            harvester._get_content_as_unicode(mock_harvest_source_url)
        assert ex.exception.message == '404 Client Error: Not Found for url: {}'.format(mock_harvest_source_url)
