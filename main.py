import argparse
import logging

from core.api import Api
from core.scraper import Scraper

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    ap = argparse.ArgumentParser()

    ap.add_argument('-e', '--endpoint',
                    default='https://api-mifit-de2.huami.com',
                    help='The URL of the regional endpoint associated with the user account')

    ap.add_argument('-t', '--token',
                    required=True,
                    help='A valid application token')

    ap.add_argument('-o', '--output-directory',
                    default='./workouts',
                    help='A directory where the downloaded workouts will be stored')

    args = vars(ap.parse_args())

    api = Api(args['endpoint'], args['token'])
    scraper = Scraper(api, args['output_directory'])
    scraper.run()
