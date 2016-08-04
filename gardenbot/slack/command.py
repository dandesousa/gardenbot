import logging
import os
import time
from slackclient import SlackClient
from gardenbot.weather import WeatherInfo, ForecastIODataSource
from gardenbot.water import WaterInfo
from geopy.geocoders import Nominatim
from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger("gardenbot-slack")


class SlackBot(object):
    def __init__(self, token, name, weather_info):
        self.client = SlackClient(token)
        self.name = name
        self._weather_info = weather_info
        self._id = self.resolve_bot_id()
        if self._id is None:
            raise RuntimeError('Unable to find a bot named {}'.format(self.name))

        self._init_commands()
        self._geolocator = Nominatim()
        self._env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")))

    def resolve_bot_id(self):
        """Finds the id for the bot user match self.name."""
        result = self.client.api_call('users.list')
        if result.get('ok'):
            users = result.get('members')
            for user in users:
                if 'name' in user and user.get('name') == self.name:
                    return user.get('id')
        return None

    @property
    def trigger_phrase(self):
        return "<@{}>:".format(self._id)

    def _init_commands(self):
        self._commands = {
            'help': self.handle_help_command,
            'water': self.handle_water_command
        }

    def handle_help_command(self, command):
        return """*beep*-bloop! My name is *@{name}*!

I'm here to give you helpful gardening advice (:smiling_imp: and other things)...

Here are a list of commands I respond to:

`@{name}: help`
`@{name}: water <address or zipcode>`
    """.format(name=self.name)

    def handle_water_command(self, command):
        address = command.replace("water ", "", 1)
        location = self._geolocator.geocode(address)
        if location is None:
            return "Unable to find location for '{}'".format(address)
        water_info = WaterInfo(location, self._weather_info)
        template = self._env.get_template('water.j2')
        return template.render(info=water_info)

    def handle_command(self, command, channel):
        """
            Receives commands directed at the bot and determines if they
            are valid commands. If so, then acts on the commands. If not,
            returns back what it needs for clarification.
        """
        response = "Not sure what you mean. Type `@{}: help` for more information.".format(self.name)
        for keyword, func in self._commands.items():
            if command.startswith(keyword):
                response = func(command)
        self.client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)

    def parse_slack_output(self, slack_rtm_output):
        """
            The Slack Real Time Messaging API is an events firehose.
            this parsing function returns None unless a message is
            directed at the Bot, based on its ID.
        """
        output_list = slack_rtm_output
        if output_list and len(output_list) > 0:
            for output in output_list:
                if output and 'text' in output and self.trigger_phrase in output['text']:
                    # return text after the @ mention, whitespace removed
                    return output['text'].split(self.trigger_phrase)[1].strip().lower(), output['channel']
        return None, None

    def run(self, websocket_delay_secs=1):
        if self.client.rtm_connect():
            logger.info("{} slack bot starting...".format(self.name))
            while True:
                command, channel = self.parse_slack_output(self.client.rtm_read())
                if command and channel:
                    self.handle_command(command, channel)
                time.sleep(websocket_delay_secs)
        else:
            logger.error('Connection failed. Invalid Slack token or bot ID?')


def get_args():
    from argparse import ArgumentParser
    parser = ArgumentParser(description="Slack bot interface for gardenbot.")
    parser.add_argument("-v", "--verbose", action="count", help="the logging verbosity (more gives more detail)")
    parser.add_argument("-n", "--name", default="gardenbot", help="Name of the bot which will be used to infer the BOT_ID")
    parser.add_argument("--api_token", default=os.environ.get('SLACK_BOT_TOKEN'), help="The slack bot api token to use. (default: %(default)s)")
    parser.add_argument("--websocket_delay_secs", default=1, type=int,
                        help="The number of seconds to wait between consecutive websocket reads. (default: %(default)s)")
    parser.add_argument("--forecast_io_api_key", default=os.environ.get('FORECAST_IO_API_KEY'),
                        help="The API for forecast IO (default: %(default)s)")
    args = parser.parse_args()

    if args.verbose == 1:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(format="%(levelname)s %(asctime)s: %(message)s")
    logger.setLevel(level)

    return args


def main():
    args = get_args()

    # source of weather data
    data_source = ForecastIODataSource(args.forecast_io_api_key)
    weather_info = WeatherInfo(data_source)

    # create our slack bot
    bot = SlackBot(args.api_token, args.name, weather_info)

    # run the bot event loop
    bot.run(args.websocket_delay_secs)


if __name__ == "__main__":
    main()
