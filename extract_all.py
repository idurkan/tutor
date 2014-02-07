import os
import itertools
import logging
import json
import subprocess

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()

# assuming that we're in the same directory as tutor's bin dir
TUTOR_DIR = os.path.realpath(os.path.dirname(__file__)) 
TUTOR_PATH = os.path.join(TUTOR_DIR, "bin/tutor")

def _query_tutor(command_parameters):
    """

    :param command_parameters:
    :return: the json-parsed output of the tutor command
    """

    command = [TUTOR_PATH, '--format', 'json'] + command_parameters

    try:
        return json.loads(subprocess.check_output(command).strip())
    except (subprocess.CalledProcessError, ValueError) as e:
        raise subprocess.CalledProcessError(u'problem with command',
                                            u' '.join(command))


def _query_tutor_for_cards_by_set(set_name):
    """
    :param set_name: the set's name, which will be passed to
        tutor's command line
    :return: a list of cards represented as dictionaries
    """

    log.debug('searching for set name: %r', set_name)
    return _query_tutor(['set', set_name])


def _query_tutor_for_all_sets():
    log.debug('searching for sets')
    return _query_tutor(['sets'])


def write_all_cards_from_gatherer_to_file():
    """
    :return: a dictionary mapping card names to the card's dictionary representation
    """
    all_sets = _query_tutor_for_all_sets()
    cards = {
        card['name']: card
        # for card in itertools.chain(*[_query_tutor_for_cards_by_set("Lorwyn")])
        for card in itertools.chain(*[_query_tutor_for_cards_by_set(set_name)
                                      for set_name in all_sets])
    }

    json.dump(cards, open('cards.json', 'wb'), indent=4, sort_keys=True, separators=(',', ': '))

if __name__ == '__main__':

    write_all_cards_from_gatherer_to_file()
