"""Multibox Orange SMS platform for notify component."""
import logging

from multibox_sms import MultiboxSmsSpider
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

import voluptuous as vol

from homeassistant.const import CONF_PASSWORD, CONF_RECIPIENT, CONF_USERNAME
import homeassistant.helpers.config_validation as cv

from homeassistant.components.notify import PLATFORM_SCHEMA, BaseNotificationService

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Required(CONF_RECIPIENT): cv.string,
    }
)

def get_service(hass, config, discovery_info=None):
    """Get the Multibox Orange SMS notification service."""
    return MultiboxSMSNotificationService(
        config[CONF_USERNAME], config[CONF_PASSWORD], config[CONF_RECIPIENT]
    )

class MultiboxSMSNotificationService(BaseNotificationService):
    """Implement a notification service for the Multibox Orange SMS service."""

    def __init__(self, username, password, recipient):
        """Initialize the service."""
        self._username = username
        self._password = password
        self._recipient = recipient

    def send_message(self, message="", **kwargs):
        """Send a SMS message via Orange.pl website."""
        try:
            spider = MultiboxSmsSpider()
            process = CrawlerProcess(get_project_settings())
            process.crawl(  spider, 
                            login = self._username, 
                            password = self._password, 
                            recipient = self._recipient, 
                            message = message
                        )
            process.start()
        except ConnectionError as ex:
            _LOGGER.error(
                "Multibox Orange SMS: unable to connect to orange.pl server.", exc_info=ex
            )
        except BaseException as ex:
            _LOGGER.error(
                "Multibox Orange SMS: error", exc_info=ex
            )
        else:
            _LOGGER.info("SMS sent")