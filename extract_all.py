import datetime
import os
import itertools
import logging
import json
import pprint
import subprocess
import sys

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


def query_cards_in_set(set_name):
    """
    :param set_name: the set's name, which will be passed to tutor's command line
    :return: a list of cards represented as dictionaries in the given set.
    """

    print "Getting set \'" + set_name + "\'..."

    start_time = get_time_now()
    json_card_list = _query_tutor(['set', set_name])

    set_cards = [_query_tutor(['card', card['id']]) for card in json_card_list]

    end_time = get_time_now()

    print('Finished getting set \'{0}\' of {1} cards; set elapsed time: {2}'.format(
        set_name, len(set_cards), str(end_time - start_time)))

    return set_cards


def query_all_sets():
    """
    :return: list of all sets reported by Gatherer.
    """
    log.debug('searching for sets')
    return _query_tutor(['sets'])


def write_cards_from_sets_to_file(target_sets):
    """
    :return: a dictionary mapping card IDs to the card's dictionary representation
    """
    cards = {
        card['id']: card
        for card in itertools.chain(*[query_cards_in_set(set_name)
                                      for set_name in target_sets])
    }

    json.dump(cards, open('cards.json', 'wb'), indent=4, sort_keys=True, separators=(',', ': '))

def check_specified_sets_exist(all_sets, spec_sets):
    for spec_set in spec_sets:
        if not spec_set in all_sets:
            return False

    return True

def get_time_now():
    return datetime.datetime.now().replace(microsecond=0)

def main(args):
    all_sets = query_all_sets()

    query_sets = args

    if not check_specified_sets_exist(all_sets, query_sets):
        print("Some of the sets you specified don't exist.  Doublecheck your arguments.")
        exit(1)

    if len(args) == 0:
        query_sets = all_sets

    start_time = get_time_now()
    print('Started scrape at: ' + str(start_time))

    write_cards_from_sets_to_file(query_sets)

    end_time = get_time_now()
    print('***************************************************')
    print('Finished scrape at: ' + str(end_time))
    print('Total elapsed time: ' + str(end_time - start_time))
    print('***************************************************')

if __name__ == '__main__':
    main(sys.argv[1:])
