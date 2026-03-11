#!/usr/bin/env -S python -X utf8

# TODO
# Add auxiliary meanings?
# Write out primary meanings and readings.
# amalgamations?

# DONE
# Added updated date.
# Added hidden_at.

from wanikani_api.client import Client, models
import json
from ruamel.yaml import YAML
import os
import requests
import sys

# Get the webm audio.
def select_audio(audios, audio_type):
    #print(len(audios))
    #print(audios)
    if len(audios) == 0:
        return None
    if len(audios) == 1:
        return audios[0]['url']
    audios_2 = list(filter(lambda x: x['content_type'] == 'audio/webm', audios))
    #print(len(audios_2))
    #print(audios_2)
    if len(audios_2) == 1:
        return audios_2[0]['url']
    audios_3 = list(filter(lambda x: x['metadata']['gender'] == audio_type, audios_2))
    #print(len(audios_3))
    #print(audios_3)
    if len(audios_3) == 1:
        return audios_3[0]['url']
    return audios_3[-1]['url']

def get_filename(url):
    fragment_removed = url.split("#")[0]  # keep to left of first #
    query_string_removed = fragment_removed.split("?")[0]
    scheme_removed = query_string_removed.split("://")[-1].split(":")[-1]
    if scheme_removed.find("/") == -1:
        return ""
    return os.path.basename(scheme_removed)

def get_entries_from_data(data):
    return [item for page in data.pages for item in page._raw['data']]


yaml=YAML(pure=True)

# Add option to read API key from a file.
#assert len(sys.argv) == 2 # needs WaniKani API key
#v2_api_key = sys.argv[1]

with open('wanikani_api_key.txt', 'r') as f:
    key = f.read().rstrip()
    client = Client(key)

folder_path = 'data/wanikani/sound'
os.makedirs(folder_path, exist_ok=True)
os.makedirs('data/wanikani/images', exist_ok=True)

# How to handle kana vocab?
# Genki has kana vocab (ex. デート), but data/genki/vocab_*.yaml does not contain any.
# 1. Update genki/vocab_*.yaml with kana vocab.  Have to create for lesson 1 and 2 also.
# 2. Create a kana vocab deck, organized by WK level(?).
# 3. Include kana vocab into Remaining deck (TODO).
kana_vocabulary = client.subjects(types="kana_vocabulary", fetch_all=True)
flat_kana_vocab = get_entries_from_data(kana_vocabulary)
del kana_vocabulary
with open(f'data/wanikani/raw_kana_vocabulary', 'w', encoding='utf-8') as f:
    print(*map(str, flat_kana_vocab), sep='\n\n', file=f)

num_kana_vocab = len(flat_kana_vocab)
#in_dict = kana_vocabulary.current_page._raw
kana_vocab_dict = {}
i = 1
latest_update = ''
for kv in flat_kana_vocab:
    _id = kv['id']
    data = kv['data']
    word = data['characters']
    meanings = [m['meaning'] for m in data['meanings']]
    meaning_mnemonic = data['meaning_mnemonic']
    usage = data['parts_of_speech']
    sentences = data['context_sentences']
    audio_url_female = select_audio(data['pronunciation_audios'], 'female')
    #audio_filename_female = get_filename(audio_url_female) if audio_url_female is not None else None
    audio_filename_female = f'{data['slug']}_female.webm' if audio_url_female is not None else None
    if audio_filename_female is not None:
        audio = requests.get(audio_url_female)
        if audio.status_code != requests.codes.ok:
            print(f'Error retrieving {word} female audio file "{audio_url_female}".')
        with open(f'data/wanikani/sound/{audio_filename_female}', 'wb') as f:
            f.write(audio.content)
    audio_url_male = select_audio(data['pronunciation_audios'], 'male')
    #audio_filename_male = get_filename(audio_url_male) if audio_url_male is not None else None
    audio_filename_male = f'{data['slug']}_male.webm' if audio_url_male is not None else None
    if audio_filename_male is not None:# and False:
        audio = requests.get(audio_url_male)
        if audio.status_code != requests.codes.ok:
            print(f'Error retrieving {word} male audio file "{audio_url_male}".')
        with open(f'data/wanikani/sound/{audio_filename_male}', 'wb') as f:
            f.write(audio.content)
    kana_vocab_dict[_id] = {
        'word': word,
        'obj_type': kv['object'],
        'meanings': meanings,
        'meaning_mnemonic': meaning_mnemonic,
        'usage': usage,
        'sentences': sentences,
        'sound_male': audio_filename_male,
        'sound_female': audio_filename_female,
        'wanikani_level': data['level'],
        'updated_date': kv['data_updated_at'],
        'hidden_at': data['hidden_at'],
    }
    if kv['data_updated_at'] > latest_update: latest_update = kv['data_updated_at']
    print(f'\rkana vocab: {i} / {num_kana_vocab}', end='')
    i += 1

# Already looping through, so just keep track myself.
#latest_date = max(r['data_updated_at'] for r in flat_kana_vocab)
#print(f'latest: {latest_date}')

del flat_kana_vocab
print ('')

with open('data/wanikani/kana_vocabulary.yaml', 'w+', encoding='utf-8') as f:
    yaml.dump(kana_vocab_dict, f)
del kana_vocab_dict

vocabulary = client.subjects(types="vocabulary", fetch_all=True)
#vocabulary = client.subjects(types="vocabulary")
flat_vocab = get_entries_from_data(vocabulary)
del vocabulary
#print(f'{flat_vocab}')
with open(f'data/wanikani/raw_vocabulary', 'w', encoding='utf-8') as f:
    print(*map(str, flat_vocab), sep='\n\n', file=f)

num_vocab = len(flat_vocab)
#in_dict = vocabulary.current_page._raw
vocab_dict = {}
i = 1
for v in flat_vocab:
    _id = v['id']
    data = v['data']
    word = data['characters']
    meanings = [m['meaning'] for m in data['meanings']]
    readings = [m['reading'] for m in data['readings']]
    components = data['component_subject_ids']
    meaning_mnemonic = data['meaning_mnemonic']
    reading_mnemonic = data['reading_mnemonic']
    usage = data['parts_of_speech']
    sentences = data['context_sentences']
    audio_url_female = select_audio(data['pronunciation_audios'], 'female')
    #audio_filename_female = get_filename(audio_url_female) if audio_url_female is not None else None
    audio_filename_female = f'{data['slug']}_female.webm' if audio_url_female is not None else None
    if audio_filename_female is not None:
        audio = requests.get(audio_url_female)
        if audio.status_code != requests.codes.ok:
            print(f'Error retrieving {word} female audio file "{audio_url_female}".')
        with open(f'data/wanikani/sound/{audio_filename_female}', 'wb') as f:
            f.write(audio.content)
    audio_url_male = select_audio(data['pronunciation_audios'], 'male')
    #audio_filename_male = get_filename(audio_url_male) if audio_url_male is not None else None
    audio_filename_male = f'{data['slug']}_male.webm' if audio_url_male is not None else None
    if audio_filename_male is not None:# and False:
        audio = requests.get(audio_url_male)
        if audio.status_code != requests.codes.ok:
            print(f'Error retrieving {word} male audio file "{audio_url_male}".')
        with open(f'data/wanikani/sound/{audio_filename_male}', 'wb') as f:
            f.write(audio.content)
    vocab_dict[_id] = {
        'word': word,
        'obj_type': v['object'],
        'meanings': meanings,
        'readings': readings,
        'components': components,
        'meaning_mnemonic': meaning_mnemonic,
        'reading_mnemonic': reading_mnemonic,
        'usage': usage,
        'sentences': sentences,
        'sound_male': audio_filename_male,
        'sound_female': audio_filename_female,
        'wanikani_level': data['level'],
        'updated_date': v['data_updated_at'],
        'hidden_at': data['hidden_at'],
    }
    if v['data_updated_at'] > latest_update: latest_update = v['data_updated_at']
    print(f'\rvocab: {i} / {num_vocab}', end='')
    i += 1
    #print('vocab')
    #print(v)
    #break

del flat_vocab
print ('')

#print(vocab_dict)
with open('data/wanikani/vocabulary.yaml', 'w+', encoding='utf-8') as f:
    yaml.dump(vocab_dict, f)
del vocab_dict

kanjis = client.subjects(types="kanji", fetch_all=True)
#kanjis = client.subjects(types="kanji")
flat_kanjis = get_entries_from_data(kanjis)
del kanjis
with open(f'data/wanikani/raw_kanji', 'w', encoding='utf-8') as f:
    print(*map(str, flat_kanjis), sep='\n\n', file=f)
num_kanjis = len(flat_kanjis)
#in_dict = kanjis.current_page._raw
kanji_dict = {}
i = 1
for k in flat_kanjis:
    _id = k['id']
    data = k['data']
    word = data['characters']
    meanings = [m['meaning'] for m in data['meanings']]
    readings_on = [m['reading'] for m in data['readings'] if m['type'] == 'onyomi']
    readings_kun = [m['reading'] for m in data['readings'] if m['type'] == 'kunyomi']
    primary_readings_on = [m['reading'] for m in data['readings'] if m['type'] == 'onyomi' and m['primary']]
    primary_readings_kun = [m['reading'] for m in data['readings'] if m['type'] == 'kunyomi' and m['primary']]
    components = data['component_subject_ids']
    similar = data['visually_similar_subject_ids']    
    meaning_mnemonic = data['meaning_mnemonic']
    meaning_hint = data['meaning_hint']
    reading_mnemonic = data['reading_mnemonic']
    reading_hint = data['reading_hint']
    kanji_dict[_id] = {
        'word': word,
        'obj_type': k['object'],
        'meanings': meanings,
        'readings_on': readings_on,
        'readings_kun': readings_kun,
        'primary_readings_on': primary_readings_on,
        'primary_readings_kun': primary_readings_kun,
        'components': components,
        'used_by': data['amalgamation_subject_ids'],
        'similar': similar,
        'meaning_mnemonic': meaning_mnemonic,
        'meaning_hint': meaning_hint,
        'reading_mnemonic': reading_mnemonic,
        'reading_hint': reading_hint,
        'wanikani_level': data['level'],
        'updated_date': k['data_updated_at'],
        'hidden_at': data['hidden_at'],
    }
    if k['data_updated_at'] > latest_update: latest_update = k['data_updated_at']
    print(f'\rkanji: {i} / {num_kanjis}', end='')
    i += 1
    #print('kanji')
    #print(k)
    #break

del flat_kanjis
print ('')

with open('data/wanikani/kanjis.yaml', 'w+', encoding='utf-8') as f:
    yaml.dump(kanji_dict, f)
del kanji_dict

radicals = client.subjects(types="radical", fetch_all=True)
#radicals = client.subjects(types="radical")
flat_radicals = get_entries_from_data(radicals)
del radicals
with open(f'data/wanikani/raw_radicals', 'w', encoding='utf-8') as f:
    print(*map(str, flat_radicals), sep='\n\n', file=f)
num_radicals = len(flat_radicals)
#in_dict = radicals.current_page._raw
radical_dict = {}
i = 1
for r in flat_radicals:
    _id = r['id']
    data = r['data']
    word = data['characters']
    meanings = [m['meaning'] for m in data['meanings']]
    meaning_mnemonic = data['meaning_mnemonic']
    image_filename = None
    if word is None:
        # WK API only delivers image/svg+xml.
        #image_url = [e['url'] for e in data['character_images'] if e['content_type'] == 'image/svg+xml' and e['metadata']['dimensions'] == '1024x1024'][0]
        image_url = [e['url'] for e in data['character_images'] if e['content_type'] == 'image/svg+xml'][0]
        image_filename = get_filename(image_url) if image_url is not None else None
        image = requests.get(image_url)
        if image.status_code != requests.codes.ok:
            print(f'\nError retrieving {data['slug']} {_id} image file "{image_url}".')
            print(f'{r}')
        else:
            print(f'\nSuccess retrieving {data['slug']} {_id} image file "{image_url}".')
        # Image file needs SVG extension to display in Anki.
        #image_filename = f'{image_filename}.svg'
        image_filename = f'{data['slug']}.svg'
        with open(f'data/wanikani/images/{image_filename}', 'wb') as f:
            f.write(image.content)
    radical_dict[_id] = {
        'word': word,
        'obj_type': r['object'],
        'used_by': data['amalgamation_subject_ids'],
        'meanings': meanings,
        'meaning_mnemonic': meaning_mnemonic,
        'image_filename': image_filename,
        'wanikani_level': data['level'],
        'updated_date': r['data_updated_at'],
        'hidden_at': data['hidden_at'],
    }
    if r['data_updated_at'] > latest_update: latest_update = r['data_updated_at']
    print(f'\rradicals: {i} / {num_radicals}', end='')
    i += 1
    #print('radical')
    #print(e)
    #break

del flat_radicals
print ('')

with open('data/wanikani/radicals.yaml', 'w+', encoding='utf-8') as f:
    yaml.dump(radical_dict, f)
del radical_dict

# Assumes actually did num_*.
#print(f'vocab: {num_vocab}\nkanji: {num_kanjis}\nradicals: {num_radicals}')
print(f'Updated {latest_update}.')
