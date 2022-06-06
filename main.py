import argparse
import logging

from src.api import Api
from src.scraper import Scraper

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    ap = argparse.ArgumentParser()

    ap.add_argument('-e', '--endpoint',
                    default='https://api-mifit.huami.com',
                    help='The endpoint to be used')

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
