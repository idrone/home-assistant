"""
Support for building a Raspberry Pi cover in HA.

Instructions for building the controller can be found here


For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/cover.rpi_gpio/
"""
import logging
from time import sleep

import voluptuous as vol

from homeassistant.components.cover import CoverDevice, PLATFORM_SCHEMA
from homeassistant.const import CONF_NAME
import homeassistant.components.rpi_gpio as rpi_gpio
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

CONF_COVERS = 'covers'
CONF_RELAY_PIN_UP = 'relay_pin_up'
CONF_RELAY_PIN_DOWN = 'relay_pin_down'
CONF_RELAY_TIME = 'relay_time'
CONF_RELAY_STEP_TIME = 'relay_step_time'
CONF_STATE_PIN_UP = 'state_pin_up'
CONF_STATE_PIN_DOWN = 'state_pin_down'
CONF_STATE_PULL_MODE = 'state_pull_mode'


DEFAULT_RELAY_TIME = .2
DEFAULT_STATE_PULL_MODE = 'UP'
DEPENDENCIES = ['rpi_gpio']

_COVERS_SCHEMA = vol.All(
    cv.ensure_list,
    [
        vol.Schema({
            CONF_NAME: cv.string,
            CONF_RELAY_PIN_UP: cv.positive_int,
            CONF_RELAY_PIN_DOWN: cv.positive_int,
            
        })
    ]
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_COVERS): _COVERS_SCHEMA,
    vol.Optional(CONF_STATE_PULL_MODE, default=DEFAULT_STATE_PULL_MODE):
        cv.string,
    vol.Optional(CONF_RELAY_TIME, default=DEFAULT_RELAY_TIME): cv.positive_int,
    vol.Optional(CONF_RELAY_STEP_TIME, default=CONF_RELAY_TIME/100): cv.positive_int,
    vol.Optional(CONF_STATE_PIN_UP, default=0): cv.positive_int,
    vol.Optional(CONF_STATE_PIN_DOWN, default=0): cv.positive_int,
})


# pylint: disable=unused-argument
def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the RPi cover platform."""
    relay_time = config.get(CONF_RELAY_TIME)
    state_pull_mode = config.get(CONF_STATE_PULL_MODE)
    
    covers = []
    covers_conf = config.get(CONF_COVERS)

    for cover in covers_conf:
        covers.append(RPiGPIOCover(
            cover[CONF_NAME], cover[CONF_RELAY_PIN_UP], cover[CONF_RELAY_PIN_DOWN], cover[CONF_STATE_PIN_UP], cover[CONF_STATE_PIN_DOWN],
            state_pull_mode, relay_time))
    add_devices(covers)


class RPiGPIOCover(CoverDevice):
    """Representation of a Raspberry GPIO cover."""

    def __init__(self, name, relay_pin_up, relay_pin_up, state_pin, state_pull_mode,
                 relay_time):
        """Initialize the cover."""
        self._name = name
        self._state_up = False
        self._state_down = False
        self._relay_pin_up = relay_pin_up
        self._relay_pin_down = relay_pin_down
        self._state_pull_mode = state_pull_mode
        self._relay_time = relay_time
        self._relay_step_time = relay_step_time
        rpi_gpio.setup_output(self._relay_pin_up)
        rpi_gpio.setup_output(self._relay_pin_down)
        if self._state_pin_up not == 0:
            rpi_gpio.setup_input(self._state_pin_up, self._state_pull_mode)
        if self._state_pin_down not == 0:
        rpi_gpio.setup_input(self._state_pin_down, self._state_pull_mode)
        

    @property
    def unique_id(self):
        """Return the ID of this cover."""
        return '{}.{}'.format(self.__class__, self._name)

    @property
    def name(self):
        """Return the name of the cover if any."""
        return self._name

    def update(self):
        """Update the state of the cover."""
        if self._state_pin_up not == 0:
        self._state_up = rpi_gpio.read_input(self._state_pin_up)
        if self._state_pin_down not == 0:
        self._state_down = rpi_gpio.read_input(self._state_pin_down)

    @property
    def is_closed(self):
        """Return true if cover is closed."""
        return self._state_down
    
    @property
    def is_opened(self):
        """Return true if cover is closed."""
        return self._state_up

    def _trigger_up(self):
        """Trigger the cover."""
        rpi_gpio.write_output(self._relay_pin_up, True)
        sleep(self._relay_step_time)
        rpi_gpio.write_output(self._relay_pin_up, False)
        
    def _trigger_down(self):
        """Trigger the cover."""
        rpi_gpio.write_output(self._relay_pin_down, True)
        sleep(self._relay_step_time)
        rpi_gpio.write_output(self._relay_pin_down, False)
        
    def close_cover(self):
        """Close the cover."""
        if not self.is_closed:
            if self._relay_pin_down == 0 :
                count = 0
                while (count < 100):
                    self._trigger_down()
                    count = count + 1
            else:
                while not self.is_closed:
                    self._trigger_down()
                    self.update()
                    
    def open_cover(self):
        """Close the cover."""
        if not self.is_opened:
            if (self._relay_pin_up == 0) :
                count = 0
                while (count < 100):
                    self._trigger_up()
                    count = count + 1
                self.is_opened = True;
            else:
                while not self.is_opened:
                    self._trigger_down()
                    self.update()
