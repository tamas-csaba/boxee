__author__ = 'tamas'
import logging
import dbus
import sys
import RPi.GPIO as GPIO
import gobject

logger = logging.getLogger()
"""
http://app.programmingfonts.org/
Inconsolata, Monaco, Consolas, 'Courier New', Courier;
"""


class GpioConnector:
    def __init__(self, out_channels=None, in_channels=None):
        logger.info('RPI board info: %s' % GPIO.RPI_INFO)
        GPIO.setmode(GPIO.BCM)
        if GPIO.getmode() != GPIO.BCM:
            logger.warn('Please note, could not set GPIO Mode to GPIO.BCM, but %s; This might create troubles around the board numbering convention' % GPIO.getmode())

        #chan_list = [11,12]
        #GPIO.setup(channel, GPIO.OUT)
        #GPIO.setup(channel, GPIO.OUT, initial=GPIO.HIGH)

        self.out_channels = out_channels
        if out_channels is not None:
            try:
                logger.info('Initializing out channels %s' % out_channels)
                GPIO.setup(out_channels, GPIO.OUT)
            except:
                logger.error('Unexpected error: %s' % sys.exc_info()[0])
                raise
        else:
            logger.warning('No output channels are initialized.')

        if in_channels is not None:
            logger.warning('Input channels are initialized, but input is not yet supported.')
        else:
            logger.warning('No input channels are initialized.')

    def open_slot(self, slot_id):
        """
        Open the slot identified by the slot_id for 1 seconds, afterwards it closing it again
        :param slot_id: the slot to be opened
        :return:
        """
        logger.debug('setting channel [%s] to HIGH', slot_id)
        GPIO.output(slot_id, GPIO.HIGH)
        gobject.timeout_add(3000, self.close_slot, slot_id)

    @staticmethod
    def close_slot(slot_id):
        try:
            logger.debug('setting channel [%s] to LOW', slot_id)
            GPIO.output(slot_id, GPIO.LOW)
        finally:
            return False

    def handle_out_channel_control_array(self, control_array):
        counter = 0
        for item in control_array:
            if isinstance(item, dbus.Byte):
                if counter < len(self.out_channels):
                    if item == 0x00:
                        logger.debug('Setting channel [%s] to LOW', self.out_channels[counter])
                        GPIO.output(self.out_channels[counter], GPIO.LOW)
                    else:
                        logger.debug('Setting channel [%s] to HIGH', self.out_channels[counter])
                        GPIO.output(self.out_channels[counter], GPIO.HIGH)
                else:
                    logger.warn('Ignoring byte value for channel which is out of initialized channel bound')

            else:
                logger.warn('Discarding non dbus.Byte control array item.')
            counter += 1

    def cleanup(self):
        GPIO.cleanup()