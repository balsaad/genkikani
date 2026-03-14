#!/usr/bin/env -S python -u -X utf8

# TODO
# https://github.com/davidluzgouveia/kanji-data
# Add error handling
#   Cannot open spreadsheet, then continue
#   Genki item is not in WK
# Filter out hidden items.  Or perhaps add hidden decks.
#   Search all WK data when trying to match Genki kanji and vocabulary.
#   Add hidden items into a seperate deck.
#   As of 2026-02-27 radicals and vocabulary have hidden items.
# Kanji Kentei (Kanken) level
#   https://www.kanken.or.jp/kanken/grades/overview/
#   https://github.com/onlyskin/kanjiapi.dev
# Option to choose male or female voice.
# Investigate handling wanikani_kanji.

# Done
# Add JLPT level (N5 - N1).
# Add grade level (1-10).  See https://www.edrdg.org/wiki/KANJIDIC_Project.html
# The "grade" of the kanji.
# - G1 to G6 indicates the grade level as specified by the Japanese Ministry of
# Education for kanji that are to be taught in elementary school (1026 Kanji).
# These are sometimes called the kyōiku (education) kanji and are part of the set
# of jōyō (daily use) kanji;
# - G8 indicates the remaining jōyō kanji that are to be taught in secondary school
# (additional 1,110 Kanji). Note that 1,106 of the G8 kanji are in the KANJIDIC file,
# a further two are in the KANJD212 file and the remaining two are only in the
# KANJIDIC2 XML file;
# - G9 and G10 indicate jinmeiyō ("for use in names") kanji which in addition to the
# jōyō kanji are approved for use in family name registers and other official
# documents. G9 (649 kanji, of which 640 are in KANJIDIC) indicates the kanji is a
# "regular" name kanji, and G10 (212 kanji of which 130 are in KANJIDIC) indicates
# the kanji is a variant of a jōyō kanji.
# Add stroke counts
# Add frequency.
# Kana vocab - Genki data does not include kana vocab, so easiest to add kana vocab
# with remaining kanji and vocab for each WK level.
# Add remaining kanji and vocab to a deck.
# Add KKLC entry number.
# Add KKLD entry number.
# Add Genki lesson number.
# Add WaniKani level

from ruamel.yaml import YAML
from typing import Any, Dict, List
from pathlib import Path
from src.anki_exporter import export_to_anki
from copy import deepcopy
import re
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

yaml=YAML()
radicals_all = yaml.load(Path('data/wanikani/radicals.yaml'))
kanjis_all = yaml.load(Path('data/wanikani/kanjis.yaml'))
vocabulary_all = yaml.load(Path('data/wanikani/vocabulary.yaml'))
kana_vocabulary_all = yaml.load(Path('data/wanikani/kana_vocabulary.yaml'))

#radicals = {k: v for k, v in radicals_all.items() if v['hidden_at'] is None}
#kanjis = {k: v for k, v in kanjis_all.items() if v['hidden_at'] is None}
#vocabulary = {k: v for k, v in vocabulary_all.items() if v['hidden_at'] is None}
#kana_vocabulary = {k: v for k, v in kana_vocabulary_all.items() if v['hidden_at'] is None}

radicals_hidden = {k: v for k, v in radicals_all.items() if v['hidden_at'] is not None}
kanjis_hidden = {k: v for k, v in kanjis_all.items() if v['hidden_at'] is not None}
vocabulary_hidden = {k: v for k, v in vocabulary_all.items() if v['hidden_at'] is not None}
kana_vocabulary_hidden = {k: v for k, v in kana_vocabulary_all.items() if v['hidden_at'] is not None}

max_wanikani_level = max(v['wanikani_level'] for v in
        (kanjis_all | radicals_all | vocabulary_all | kana_vocabulary_all).values())

# kanji.json from https://github.com/davidluzgouveia/kanji-data
# Source of strokes, JLPT level, and grade level information.
with open('data/kanji.json', 'r', encoding="utf-8") as f:
    k_info = json.load(f)

def find_vocab(vocab:str) -> Dict[str, Any]:
    try:
        return next(obj for key, obj in vocabulary_all.items() if obj['word'] == vocab)
    except StopIteration:
        return None

def unique(l):
    # requires python 3.7 for order
    return list(dict.fromkeys(l))

def kanji_to_id(kanji:str)->int:
    first = next(k for k,v in kanjis_all.items() if v['word'] == kanji)
    assert first is not None
    return first

def get_radicals_for_kanji(kanji:int) -> List[int]:
    #kanji_data = kanjis[kanji]
    #return kanji_data['components']
    return kanjis_all[kanji]['components']

def mark_important(kanas:str) -> str:
    return f'<span style="background-color: rgba(235, 84, 5, 0.1);">{kanas}</span>'

def get_radical_or_img_tag(c:dict, big:bool = False):
    return c['word'] if c['word'] is not None else f"<img class=\"{'big'if big else 'small'}\" src=\"{c['image_filename']}\">"

def perform_vocab_transformations(vocab_data): # kinda bad name

    if 'sound' not in vocab_data:
        del vocab_data['sound_male']
        vocab_data['sound'] = vocab_data['sound_female']
        del vocab_data['sound_female']

    if vocab_data['sound'] is None:
        #print(f'No audio for {vocab_data}.')
        print(f'No audio for {vocab_data['word']} {vocab_data['meanings']}.')
        vocab_data['sound'] = ''

    if 'sentences' not in vocab_data:
        vocab_data['sentences'] = ''
        #print(f'No sentences for {vocab_data}.')
    else:
        sentences = []
        for s in vocab_data['sentences']:
            sentences.append(f"{s['ja']} ({s['en']}))")
        vocab_data['sentences'] = "<br>".join(sentences)

    if 'usage' not in vocab_data:
        vocab_data['type'] = ''
        #print(f'No usage for {vocab_data}')
    else:
        vocab_data['type'] = '<br>'.join(vocab_data['usage'])
        del vocab_data['usage']

    if 'components' not in vocab_data:
        component_ids = []
        component_data = []
    else:
        component_ids = vocab_data['components']
        component_data = [kanjis_all[i] for i in component_ids]

    vocab_data['kanjis'] = ' '.join([k['word'] for k in component_data])
    vocab_data['kanjis_names'] = ', '.join([k['meanings'][0] for k in component_data])

def main():# Define the scope
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive',
    ]

    # Add your service account JSON key file name here
    creds = ServiceAccountCredentials.from_json_keyfile_name('genkikani-f83049e05c40.json', scope)
    client = gspread.authorize(creds)

    # Open the Google Sheet by title or URL
    # Source of KKLC and KKLD information.
    spreadsheet = client.open('Kodansha Kanji Learner Course/Dictionary')
    sheet = spreadsheet.worksheet('KKLC/D')

    # Source of kanji frequency data.
    spreadsheet2 = client.open('2242 KANJI FREQUENCY LIST VER. 1.1')
    sheet2 = spreadsheet2.worksheet('MAIN')

    # Read data from the Google Sheet
    ss_data = sheet.get_all_records()
    ss_data2 = sheet2.get_all_records()

    genki_dir = Path('data/genki/')
    already_included_radicals = []
    lections = []
    images = []
    already_learned_kanji_ids = set()
    already_learned_vocab_ids = set()
    already_learned_wanikani_vocab_ids = set()
    no_kklc_count = 0
    for f in filter(lambda x: x.name.startswith('kanji'), sorted(genki_dir.iterdir())):
        # Extract genki lesson number from file name.
        # Assumes lesson number is embedded in file name as first matching num in path name.
        match = re.search(r'\d+', str(f))
        genki_lesson_num = int(match.group(0))
        lection_data = yaml.load(f)
        vocab_lection_path = f.parent / f.name.replace('kanjis', 'vocab')
        if vocab_lection_path.exists() == False: break
        vocab_lection_data = yaml.load(vocab_lection_path)
        lection_kanjis = [k['kanji'] for k in lection_data]
        lection_kanji_ids = [kanji_to_id(k) for k in lection_kanjis]
        required_radicals = unique([radical for kanji in lection_kanji_ids for radical in get_radicals_for_kanji(kanji)])
        required_radicals = [x for x in required_radicals if x not in already_included_radicals]
        already_included_radicals.extend(required_radicals)

        genkikani_radicals = []
        for rad_id in required_radicals:
            rad_data = deepcopy(radicals_all[rad_id])
            rad_data['word'] = get_radical_or_img_tag(rad_data, True)
            if rad_data['image_filename'] is not None:
                images.append(rad_data['image_filename'])
            #del rad_data['image_filename']
            if 'wanikani_level' not in rad_data:
                # Inconsistency in WK data.
                print(f'No WaniKani level for radical {rad_data['word']} in Genki lesson {genki_lesson_num}')
                rad_data['wanikani_level'] = ''
            else:
                rad_data['wanikani_level'] = str(rad_data['wanikani_level'])
            #rad_data['Tags'] = 'rtest rtest2'
            genkikani_radicals.append(rad_data)

        genkikani_kanjis = []
        for kanji_id, genki_data in zip(lection_kanji_ids, lection_data):
            kanji_data = deepcopy(kanjis_all[kanji_id])
            onyomi_readings = genki_data.get('onyomi', [])
            if onyomi_readings is None: onyomi_readings = []
            important_onyomi = [reading['reading'] for reading in onyomi_readings if reading['important'] == True]
            kunyomi_readings = genki_data.get('kunyomi', [])
            if kunyomi_readings is None: kunyomi_readings = []
            important_kunyomi = [reading['reading'] for reading in kunyomi_readings if reading['important'] == True]
            kanji_data['readings_on'] = [reading if reading not in important_onyomi else mark_important(reading) for reading in kanji_data['readings_on']]
            kanji_data['readings_kun'] = [reading if reading not in important_kunyomi else mark_important(reading) for reading in kanji_data['readings_kun']]
            # convert components to radicals
            component_ids = kanji_data['components']
            component_data = [radicals_all[i] for i in component_ids]
            kanji_data['radicals'] = ' '.join([get_radical_or_img_tag(r, False) for r in component_data])
            kanji_data['radicals_names'] = ', '.join([r['meanings'][0] for r in component_data])

            similar_kanji_ids = kanji_data['similar']
            similar_kanji_data = [kanjis_all[i] for i in similar_kanji_ids]
            kanji_data['similar_kanji'] = ' '.join([k['word'] for k in similar_kanji_data])
            kanji_data['similar_kanji_names'] = ', '.join([k['meanings'][0] for k in similar_kanji_data])

            kanji_data['genki_lesson_num'] = str(genki_lesson_num)
            if 'wanikani_level' not in kanji_data:
                # Inconsistency in WK data.
                print(f'No WaniKani level for kanji {genki_lesson_num} {kanji_data['word']}')
                kanji_data['wanikani_level'] = ''
            else:
                kanji_data['wanikani_level'] = str(kanji_data['wanikani_level'])
            kk_data = next((item for item in ss_data if item["Kanji"] == kanji_data['word']),
                        {'KKLC': '', 'KKLD (2 ed.)': '', 'SKIP code': ''})
            freq_data = next((item for item in ss_data2 if item["FORM"] == kanji_data['word']),
                        {'Relative freq from big 5': ''})
            if kk_data['KKLC'] == '':
                # Don't count the "repeater" kanji.
                if kanji_data['word'] != '々':
                    print(f'{kanji_data['word']} {kanji_data['meanings']} {kanji_data['wanikani_level']} no KKLC data.')
                    no_kklc_count += 1
            kanji_data['KKLC'] = str(kk_data['KKLC'])
            kanji_data['KKLD_2ed'] = str(kk_data['KKLD (2 ed.)'])
            kanji_data['KKLD_SKIP_code'] = str(kk_data['SKIP code'])
            kanji_data['frequency'] = str(freq_data['Relative freq from big 5'])
            kanji_data['strokes'] = str(k_info.get(kanji_data['word'], {}).get('strokes', ''))
            kanji_data['grade'] = str(k_info.get(kanji_data['word'], {}).get('grade', ''))
            kanji_data['jlpt'] = str(k_info.get(kanji_data['word'], {}).get('jlpt_new', ''))
            genkikani_kanjis.append(kanji_data)
            already_learned_kanji_ids.add(kanji_id)

        genkikani_vocabs_important = []
        genkikani_vocabs_unimportant = []
        vocab_not_found_count = 0
        # Genki vocab
        for vocab_entry in vocab_lection_data:
            wanikani_data = None
            vocab_data = None
            exists_in_wanikani = False
            id = None
            try:
                id, wanikani_data = next((key,obj) for key, obj in vocabulary_all.items() if obj['word'] == vocab_entry['kanji'])
                exists_in_wanikani = True
                vocab_data = deepcopy(wanikani_data)
            except StopIteration:
                try:
                    if 'wanikani_kanji' not in vocab_entry: raise StopIteration()
                    id, wanikani_data = next((key,obj) for key, obj in vocabulary_all.items() if obj['word'] == vocab_entry['wanikani_kanji'])
                    exists_in_wanikani = True
                    vocab_data = deepcopy(wanikani_data)
                    vocab_data['full_kanji'] = vocab_data['word']
                    vocab_data['word'] = vocab_entry['kanji']
                    vocab_data['note'] = vocab_entry['note']
                except StopIteration:
                    # Fall back to Genki data.
                    try:
                        vocab_data = {
                            'word': vocab_entry['kanji'],
                            'meanings': [vocab_entry['meaning']],
                            'readings': [vocab_entry['kana']],
                            'components': [e for e in [next((key for key, obj in kanjis_all.items() if obj['word'] == k), None) for k in vocab_entry['kanji']] if e is not None],
                            'meaning_mnemonic': '',
                            'reading_mnemonic': '',
                            'sound': '',
                            'wanikani_level': '',
                        }
                        print(f'No WaniKani data for vocabulary {vocab_entry['kanji']} {vocab_entry['meaning']} - using Genki data.')
                    except StopIteration:
                        print(f'Can\'t find data for vocabulary {vocab_entry["kanji"]} {vocab_entry['meaning']}.')
                        vocab_not_found_count += 1

            perform_vocab_transformations(vocab_data)
            # Due to radicals, component kanji, etc., this lesson num does not mean the
            # kanji is actually in this Genki lesson.
            vocab_data['genki_lesson_num'] = str(genki_lesson_num)
            if 'wanikani_level' not in vocab_data:
                print(f'No WaniKani level for vocabulary {genki_lesson_num} {vocab_data['word']}.')
                vocab_data['wanikani_level'] = ''
            else:
                vocab_data['wanikani_level'] = str(vocab_data['wanikani_level'])
            #vocab_data['Tags'] = 'vtest vtest2'

            have_learned_component_kanji = False
            if exists_in_wanikani:
                #have_learned_component_kanji = len(set(wanikani_data['components']) & already_learned_kanji_ids) == len(wanikani_data['components'])
                have_learned_component_kanji = set(wanikani_data['components']).issubset(already_learned_kanji_ids)
            if vocab_entry.get('important', False) == True or exists_in_wanikani and have_learned_component_kanji:
                genkikani_vocabs_important.append(vocab_data)
                if exists_in_wanikani:
                        already_learned_vocab_ids.add(id)
            else:
                genkikani_vocabs_unimportant.append(vocab_data)

        # WaniKani vocab using kanjis from this and previous lessons.
        additional_wanikani_vocab = []
        #for id, v in vocabulary.items():
        for id, v in vocabulary_all.items():
            # Do not include hidden items.
            if v['hidden_at'] is not None: continue
            if id in already_learned_vocab_ids or id in already_learned_wanikani_vocab_ids: continue
            #if len(set(v['components']) & already_learned_kanji_ids) == len(v['components']):
            if set(v['components']).issubset(already_learned_kanji_ids):
                already_learned_wanikani_vocab_ids.add(id)
                vocab_data = deepcopy(v)
                perform_vocab_transformations(vocab_data)
                vocab_data['genki_lesson_num'] = str(genki_lesson_num)
                if 'wanikani_level' not in vocab_data:
                    # This would be weird since getting from WK data.
                    print(f'No WaniKani level for vocabulary {genki_lesson_num} {vocab_data['word']}')
                    vocab_data['wanikani_level'] = ''
                else:
                    vocab_data['wanikani_level'] = str(vocab_data['wanikani_level'])
                #vocab_data['Tags'] = 'vtest vtest2'
                additional_wanikani_vocab.append(vocab_data)

        # important: Genki important vocabulary.
        # unimportant: Genki unimportant vocabulary.
        # wanikani: WK vocabulary that use this and previous lessons kanji.
        lections.append({
            'name': f'Genki lesson {f.name.split(".")[0].split("_")[1]}',
            'radicals': genkikani_radicals,
            'kanjis': genkikani_kanjis,
            'vocabulary_important': genkikani_vocabs_important,
            'vocabulary_wanikani': additional_wanikani_vocab,
            'vocabulary_unimportant': genkikani_vocabs_unimportant,
        })

    # Get all the radicals not used in Genki.
    #print(f'Included radicals {len(already_included_radicals)}: {already_included_radicals}')
    remaining_radical = [x for x in radicals_all if x not in already_included_radicals]
    #print(f'Remaining radicals {len(remaining_radical)}: {remaining_radical}')
    print(f'Remaining radicals {len(remaining_radical)}.')

    #print(f'Learned kanji {len(already_learned_kanji)}: {already_learned_kanji_ids}')
    remaining_kanji = [x for x in kanjis_all if x not in already_learned_kanji_ids]
    #print(f'Remaining kanji {len(remaining_kanji)}: {remaining_kanji}')
    #print(f'Remaining kanji {len(remaining_kanji)}: {remaining_kanji}')
    print(f'Remaining kanji {len(remaining_kanji)}.')

    remaining_vocab = [x for x in vocabulary_all if x not in already_learned_vocab_ids]
    #print(f'Remaining vocab {len(remaining_vocab)}: {remaining_vocab}')
    print(f'Remaining vocab {len(remaining_vocab)}.')

    print(f'Kana vocab {len(kana_vocabulary_all)}.')

    # Organize the remaining radicals, kanji, vocab by WaniKani level.
    # Frequency better?

    for wk_level in range(1, max_wanikani_level + 1):
        remaining_radicals_in_level = []
        remaining_radicals_hidden_in_level = []
        radicals_in_level = [x for x in remaining_radical if radicals_all[x]['wanikani_level'] == wk_level]
        for rad in radicals_in_level:
            rad_data = deepcopy(radicals_all[rad])
            rad_data['word'] = get_radical_or_img_tag(rad_data, True)
            if rad_data['image_filename'] is not None:
                images.append(rad_data['image_filename'])
            #del rad_data['image_filename']
            rad_data['wanikani_level'] = str(wk_level)
            if rad_data['hidden_at'] is None:
                remaining_radicals_in_level.append(rad_data)
            else:
                remaining_radicals_hidden_in_level.append(rad_data)

        remaining_kanjis_in_level = []
        remaining_kanjis_hidden_in_level = []
        kanjis_in_level = [x for x in remaining_kanji if kanjis_all[x]['wanikani_level'] == wk_level]
        for kanji in kanjis_in_level:
            kanji_data = deepcopy(kanjis_all[kanji])
            onyomi_readings = kanji_data['readings_on']
            important_onyomi = []
            kunyomi_readings = kanji_data['readings_kun']
            important_kunyomi = []
            kanji_data['readings_on'] = [reading if reading not in important_onyomi else mark_important(reading) for reading in kanji_data['readings_on']]
            kanji_data['readings_kun'] = [reading if reading not in important_kunyomi else mark_important(reading) for reading in kanji_data['readings_kun']]
            # convert components to radicals
            component_ids = kanji_data['components']
            component_data = [radicals_all[i] for i in component_ids]
            kanji_data['radicals'] = ' '.join([get_radical_or_img_tag(r, False) for r in component_data])
            kanji_data['radicals_names'] = ', '.join([r['meanings'][0] for r in component_data])

            similar_kanji_ids = kanji_data['similar']
            # I think there is some error in WK data.  9397 does not exist
            #similar_kanji_data = [kanjis[i] for i in similar_kanji_ids]
            similar_kanji_data = []
            for i in similar_kanji_ids:
                if i in kanjis_all:
                    similar_kanji_data.append(kanjis_all[i])
                else:
                    print(f'Not found: Kanji {i} for similar kanji from {kanji_data}.')
            kanji_data['similar_kanji'] = ' '.join([k['word'] for k in similar_kanji_data])
            kanji_data['similar_kanji_names'] = ', '.join([k['meanings'][0] for k in similar_kanji_data])
            if kanji_data['meaning_hint'] is None:
                kanji_data['meaning_hint'] = ''

            kanji_data['genki_lesson_num'] = ''
            kanji_data['wanikani_level'] = str(wk_level)
            kk_data = next((item for item in ss_data if item["Kanji"] == kanji_data['word']),
                        {'KKLC': '', 'KKLD (2 ed.)': '', 'SKIP code': ''})
            freq_data = next((item for item in ss_data2 if item["FORM"] == kanji_data['word']),
                        {'Relative freq from big 5': ''})
            if kk_data['KKLC'] == '':
                # Don't count the "repeater" kanji.
                if kanji_data['word'] != '々':
                    print(f'{kanji_data['word']} {kanji_data['meanings']} WK level {kanji_data['wanikani_level']} no KKLC data.')
                    no_kklc_count += 1
            kanji_data['KKLC'] = str(kk_data['KKLC'])
            kanji_data['KKLD_2ed'] = str(kk_data['KKLD (2 ed.)'])
            kanji_data['KKLD_SKIP_code'] = str(kk_data['SKIP code'])
            kanji_data['frequency'] = str(freq_data['Relative freq from big 5'])
            kanji_data['strokes'] = str(k_info.get(kanji_data['word'], {}).get('strokes', ''))
            kanji_data['grade'] = str(k_info.get(kanji_data['word'], {}).get('grade', ''))
            kanji_data['jlpt'] = str(k_info.get(kanji_data['word'], {}).get('jlpt_new', ''))

            if kanji_data['hidden_at'] is None:
                remaining_kanjis_in_level.append(kanji_data)
            else:
                remaining_kanjis_hidden_in_level.append(kanji_data)

        remaining_vocab_in_level = []
        remaining_vocab_hidden_in_level = []
        vocab_in_level = [x for x in remaining_vocab if vocabulary_all[x]['wanikani_level'] == wk_level]
        for vocab in vocab_in_level:
            vocab_data = deepcopy(vocabulary_all[vocab])

            vocab_data['genki_lesson_num'] = ''
            vocab_data['wanikani_level'] = str(wk_level)
            perform_vocab_transformations(vocab_data)

            if vocab_data['hidden_at'] is None:
                remaining_vocab_in_level.append(vocab_data)
            else:
                remaining_vocab_hidden_in_level.append(vocab_data)

        # No info on Genki kana vocab, so list all WK kana vocab in the level.
        kana_vocab_in_level = []
        kana_vocab_hidden_in_level = []
        kana_vocab_ids_in_level = [x for x in kana_vocabulary_all if kana_vocabulary_all[x]['wanikani_level'] == wk_level]
        #print(f'WK level: {wk_level} {len(kana_vocab_in_level)} kana vocab: {kana_vocab_in_level}')
        for i in kana_vocab_ids_in_level:
            kana_vocab_data = deepcopy(kana_vocabulary_all[i])

            kana_vocab_data['genki_lesson_num'] = ''
            kana_vocab_data['wanikani_level'] = str(wk_level)
            # Not sure if better to use vocab template (and fill in the missing
            #fields) or create kana vocab template.
            kana_vocab_data['readings'] = []
            kana_vocab_data['reading_mnemonic'] = ''
            perform_vocab_transformations(kana_vocab_data)

            if kana_vocab_data['hidden_at'] is None:
                kana_vocab_in_level.append(kana_vocab_data)
            else:
                kana_vocab_hidden_in_level.append(kana_vocab_data)

        #print(f'WK level {wk_level} remaining radicals count: {len(remaining_radicals_in_level)}', flush=True)
        #print(f'WK level {wk_level} remaining kanjis count: {len(remaining_kanjis_in_level)}', flush=True)
        #print(f'WK level {wk_level} remaining vocabulary count: {len(remaining_vocab_in_level)}', flush=True)
        #print(f'WK level {wk_level} kana vocabulary count: {len(kana_vocab_in_level)}', flush=True)

        lections.append({
            'name': f'WK level {wk_level:02}',
            'radicals': remaining_radicals_in_level,
            'radicals_hidden': remaining_radicals_hidden_in_level,
            'kanjis': remaining_kanjis_in_level,
            'kanjis_hidden': remaining_kanjis_hidden_in_level,
            'vocabulary': remaining_vocab_in_level,
            'vocabulary_hidden': remaining_vocab_hidden_in_level,
            'kana_vocabulary': kana_vocab_in_level,
            'kana_vocabulary_hidden': kana_vocab_hidden_in_level,
        })

    print(f"Can't find data for {vocab_not_found_count} vocabulary.")
    print(f'{no_kklc_count} kanji with no KKLC data.')
    print(f'{len(radicals_hidden)} hidden radicals.')
    print(f'{len(kanjis_hidden)} hidden kanji.')
    print(f'{len(vocabulary_hidden)} hidden vocabulary.')
    print(f'{len(kana_vocabulary_hidden)} hidden kana vocabulary.')

    # generate Anki decks.
    export_to_anki(lections, images)

# End main.

if __name__ == "__main__":
    raise SystemExit(main());
