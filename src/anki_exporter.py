import genanki
from typing import List

styling="""
@font-face {
    font-family: "Hiragino Kaku Gothic Pro W3";
    src: url("_hirakakyprow3.otf");
}

radical {
    color: #0a9ce6;
}

kanji {
    color: #b8046c;
}

vocabulary {
    color: #a900fd;
}

.card {
    font-family: arial;
    font-size: 20px;
    text-align: center;
    color: black;
    background-color: white;
}

.big {
    #height: 180px;
    height: 100px;
    filter: invert(100%);
}

.small {
    height: 20px;
    filter: invert(100%);
}

.radical {
    font-family: "Hiragino Kaku Gothic Pro W3";
    #font-size:180px;
    font-size:100px;
    color: white;
    background-color:#0a9ce6;
}

.kanji {
    font-family: "Hiragino Kaku Gothic Pro W3";
    #font-size:180px;
    font-size:100px;
    color: white;
    background-color:#b8046c;
}

.vocab {
    font-family: "Hiragino Kaku Gothic Pro W3";
    #font-size:180px;
    font-size:100px;
    color: white;
    background-color:#a900fd;
}

.hiragana {
    font-family: "Hiragino Kaku Gothic Pro W3";
    font-size: 25 px;
}

.text {
    #font-family: "Roboto", "HelveticaNeueLT Std Lt";
    font-family: "Sitka", "Gill Sans MT", "Franklin Gothic";
    font-size:22px;
    #font-style: "italics";
}

.radicon {
    color:white;
    font-size:180px;
}

.quest-radical{
    background: #e9e9e9;
    color: #555;
    line-height: 40px;
}

.quest-kanji{
    background: #e9e9e9;
    color: #555;
    line-height: 40px;
}

.quest-vocab{
    background: #e9e9e9;
    color: #555;
    line-height: 40px;
}

#typeans {
    font-size: 20px !important;
    font-family: "Consolas" !important;
    text-align: center !important;
}
"""

radical_frontside="""
<div class="radical">{{word}}</div>

<div class="quest-radical"><b>Radical Name</b></div>

<br><br>
{{type:meanings}}
"""

radical_backside="""
{{FrontSide}}

<br><br>
<span class="text"><u><b>Meaning</b></u></span><br><br>
<span class="text"><font size="40px" color="#0a9ce6">{{meanings}}</font></span>
<br><br>
<span class="text"><u><b>Mnemonic:</b></u>&nbsp;{{meaning_mnemonic}}</span>

<br><br>
<span class="text">WaniKani level: {{wanikani_level}}</span>
"""

kanji_frontside="""
<div class="kanji">{{word}}</div>

<div class="quest-kanji"><b>Kanji Meaning</b></div>

<br><br>
{{type:meanings}}
"""

kanji_backside="""
{{FrontSide}}

<br><br>
<span class="text"><u><b>Meaning</b></u></span><br>
<span class="text"><font size="40px" color="#b8046c">{{meanings}}</font></span>
<br>
<br>
<span class="text"><u><b>On'yomi</b></u></span><br>
<span class="text"><font size="40px" color="#b8046c">{{readings_on}}</font></span>
<br>
<br>
<span class="text"><u><b>Kun'yomi</b></u></span><br>
<span class="text"><font size="40px" color="#b8046c">{{readings_kun}}</font></span>
<br>
<br>
<span class="text"><b>Radicals:</b>&nbsp;</span><font color="#b8046c"><span class="hiragana"><b>{{radicals}}</b></span></font><span class="text"> ({{radicals_names}})</span>
<br>
{{#similar_kanji}}
<br>
<span class="text"><b>Similar looking kanji:</b> </span><font color="#b8046c"><span class="hiragana"><b>{{similar_kanji}}</b></span></font><span class="text"> ({{similar_kanji_names}})</span>
<br>
{{/similar_kanji}}
<br>
<span class="text"><u><b>Meaning Mnemonic:</b></u>&nbsp;{{meaning_mnemonic}}</span>
<br>
<br>
<span class="text">{{meaning_hint}}</span>
<br>
<br>
<span class="text"><u><b>Reading Mnemonic:</b></u>&nbsp;{{reading_mnemonic}}</span>
<br>
<br>
<span class="text">{{reading_hint}}</span>

<br><br>
<span class="text">Frequency: {{frequency}}, WaniKani level: {{wanikani_level}}, Genki lesson: {{genki_lesson_num}}, KKLC entry: {{KKLC}}, KKLD 2 ed. entry: {{KKLD_2ed}}</span>
<br>
<span class="text">JLPT: {{jlpt}}, grade: {{grade}}, strokes: {{strokes}}, KKLD SKIP code: {{KKLD_SKIP_code}}</span>
"""

vocab_frontside="""
<div class="vocab">{{word}}</div>

<div class="quest-vocab"><b>Vocabulary Meaning</b></div>

<br><br>
{{type:meanings}}
"""

# TODO: sound does not exist case
vocab_backside="""
{{FrontSide}}

{{#full_kanji}}
<span class="text"><u><b>Full Kanji Version</b></u></span><br>
<span class="text">{{full_kanji}}</span>
<br>
{{/full_kanji}}

<br><br>
<span class="text"><u><b>Meaning</b></u></span><br>
<span class="text"><font size="40px" color="#a900fd">{{meanings}}</font></span>
<br>
<br>
<span class="text"><u><b>Reading</b></u></span><br>
<span class="text"><font size="40px" color="#a900fd">{{readings}}</font></span>
<br>
{{#type}}
<br>
<span class="text"><u><b>Type</b></u>:&nbsp;{{type}}</span>
<br>
{{/type}}
<br>
<span class="text"><u><b>Kanjis:</b></u>&nbsp;</span><font color="#a900fd"><span class="hiragana"><b>{{kanjis}}</b></span></font><span class="text"> ({{kanjis_names}})</span>
<br>
{{#meaning_mnemonic}}
<br>
<span class="text"><u><b>Meaning Mnemonic</b></u>:&nbsp;{{meaning_mnemonic}}</span>
<br>
{{/meaning_mnemonic}}
{{#reading_mnemonic}}
<br>
<span class="text"><u><b>Reading Mnemonic</b></u>:&nbsp;{{reading_mnemonic}}</span>
{{/reading_mnemonic}}
{{#note}}
<br>
<span class="text"><u><b>Note</b></u>:&nbsp;{{note}}</span>
<br>
{{/note}}
<br>
{{#sentences}}
<br>
<span class="text"><u><b>Sentences</b></u><br>
{{sentences}}</span>
<br>
{{/sentences}}
<br>
<span class="text">WaniKani level: {{wanikani_level}}, Genki lesson: {{genki_lesson_num}}</span>
<br>
<br>
{{#sound}}
{{sound}}
{{/sound}}
"""

vocab_reading_frontside="""
<div class="vocab">{{word}}</div>

<div class="quest-vocab"><b>Vocabulary Reading</b></div>

<br><br>
{{type:readings}}
"""

vocab_reading_backside="""
{{FrontSide}}

{{#full_kanji}}
<span class="text"><u><b>Full Kanji Version</b></u></span><br>
<span class="text">{{full_kanji}}</span>
<br>
{{/full_kanji}}

<br>
<span class="text"><u><b>Reading</b></u></span><br>
<span class="text"><font size="40px" color="#a900fd">{{readings}}</font></span>
<br>
<br>
<span class="text"><u><b>Meaning</b></u></span><br>
<span class="text"><font size="40px" color="#a900fd">{{meanings}}</font></span>
<br>
{{#type}}
<br>
<span class="text"><u><b>Type:</b></u>&nbsp;{{type}}</span>
<br>
{{/type}}
<br>
<span class="text"><b>Kanjis:</b></span>&nbsp;<font color="#a900fd"><span class="hiragana"><b>{{kanjis}}</b></span></font>&nbsp;<span class="text">({{kanjis_names}})</span>
<br>
{{#meaning_mnemonic}}
<br>
<span class="text"><u><b>Meaning Mnemonic:</b></u>&nbsp;{{meaning_mnemonic}}</span>
<br>
{{/meaning_mnemonic}}
{{#reading_mnemonic}}
<br>
<span class="text"><u><b>Reading Mnemonic:</b></u>&nbsp;{{reading_mnemonic}}</span>
<br>
{{/reading_mnemonic}}
{{#note}}
<br>
<span class="text"><u><b>Note:</b></u>&nbsp;{{note}}</span>
<br>
{{/note}}
<br>
{{#sentences}}
<br>
<span class="text"><u><b>Sentences</b></u></span><br>
<span class="text">{{sentences}}</span>
<br>
{{/sentences}}
<br>

<span class="text">WaniKani level: {{wanikani_level}}, Genki lesson: {{genki_lesson_num}}</span>
<br>
<br>
{{#sound}}
{{sound}}
{{/sound}}
"""

kana_vocab_frontside="""
<div class="vocab">{{word}}</div>

<div class="quest-vocab"><b>Vocabulary Meaning</b></div>

<br><br>
{{type:meanings}}
"""

# TODO: sound does not exist case
kana_vocab_backside="""
{{FrontSide}}

<br><br>
<span class="text"><u><b>Meaning</b></u></span><br>
<span class="text"><font size="40px" color="#a900fd">{{meanings}}</font></span>
<br>
<br>
{{#type}}
<span class="text"><u><b>Type:</b></u>&nbsp;{{type}}</span>
<br>
{{/type}}
{{#meaning_mnemonic}}
<br>
<span class="text"><u><b>Meaning Mnemonic:</b></u>&nbsp;{{meaning_mnemonic}}</span>
{{/meaning_mnemonic}}
<br><br>
{{#note}}
<br>
<span class="text"><u><b>Note:</b></u>&nbsp;{{note}}</span>
<br>
{{/note}}
{{#sentences}}
<span class="text"><u><b>Sentences</b></u></span><br>
<span class="text">{{sentences}}</span>
<br>
<br>
{{/sentences}}
<span class="text">WaniKani level: {{wanikani_level}}</span>
<br>
<br>
{{#sound}}
{{sound}}
{{/sound}}
"""

class GenkiNoteRadical(genanki.Note):
    @property
    def guid(self):
        return genanki.guid_for(self.fields[3]) # uid

class GenkiNoteKanji(genanki.Note):
    @property
    def guid(self):
        return genanki.guid_for(self.fields[12]) # uid

class GenkiNoteVocab(genanki.Note):
    @property
    def guid(self):
        return genanki.guid_for(self.fields[12]) # uid

class GenkiNoteKanaVocab(genanki.Note):
    @property
    def guid(self):
        return genanki.guid_for(self.fields[7]) # uid

def gen_vocab_deck(deck, deckpath: str, model: genanki.Model, uuid:int, sounds:List[str]) -> genanki.Deck:
    full_name = f'{deckpath}'
    anki_deck = genanki.Deck(uuid, full_name)
    for c in deck:
        note = GenkiNoteVocab(
            model=model,
            fields=[
                ", ".join(c['meanings']),
                c['word'],
                ", ".join(c['readings']),
                c['meaning_mnemonic'],
                c['reading_mnemonic'],
                c['kanjis'],
                c['kanjis_names'],
                c['type'],
                c['sentences'],
                c['note'] if 'note' in c else '',
                c['full_kanji'] if 'full_kanji' in c else '',
                f"[sound:{c['sound']}]" if c['sound'] != '' else '',
                f'{full_name}::{", ".join(c["meanings"])}',
                c['genki_lesson_num'],
                c['wanikani_level'],
                #c['Tags'],
            ],
        )
        if c['sound'] != '':
            sounds.append(c['sound'])
        anki_deck.add_note(note)
    return anki_deck

def gen_kana_vocab_deck(deck, deckpath: str, model: genanki.Model, uuid:int, sounds:List[str]) -> genanki.Deck:
    full_name = f'{deckpath}'
    anki_deck = genanki.Deck(uuid, full_name)
    for c in deck:
        note = GenkiNoteKanaVocab(
            model=model,
            fields=[
                ", ".join(c['meanings']),
                c['word'],
                c['meaning_mnemonic'],
                c['type'],
                c['sentences'],
                c['note'] if 'note' in c else '',
                f"[sound:{c['sound']}]" if c['sound'] != '' else '',
                f'{full_name}::{", ".join(c["meanings"])}',
                c['genki_lesson_num'],
                c['wanikani_level'],
                #c['Tags'],
            ],
        )
        if c['sound'] != '':
            sounds.append(c['sound'])
        anki_deck.add_note(note)
    return anki_deck

def gen_kanji_deck(deck, deckpath: str, model: genanki.Model, uuid:int) -> genanki.Deck:
    full_name = f'{deckpath}'
    anki_deck = genanki.Deck(uuid, full_name)
    for c in deck:
        note = GenkiNoteKanji(
            model=model,
            fields=[
                ", ".join(c['meanings']),
                c['word'],
                ", ".join(c['readings_on']),
                ", ".join(c['readings_kun']),
                c['meaning_mnemonic'],
                c['meaning_hint'],
                c['reading_mnemonic'],
                c['reading_hint'],
                c['radicals'],
                c['radicals_names'],
                c['similar_kanji'],
                c['similar_kanji_names'],
                f'{full_name}::{", ".join(c["meanings"])}',
                c['genki_lesson_num'],
                c['wanikani_level'],
                c['KKLC'],
                c['KKLD_2ed'],
                c['frequency'],
                c['strokes'],
                c['grade'],
                c['jlpt'],
                c['KKLD_SKIP_code'],
                #c['Tags'],
            ],
        )
        anki_deck.add_note(note)
    return anki_deck

def gen_radical_deck(deck, deckpath: str, model: genanki.Model, uuid:int) -> genanki.Deck:
    full_name = f'{deckpath}'
    anki_deck = genanki.Deck(uuid, full_name)
    for c in deck:
        note = GenkiNoteRadical(
            model=model,
            fields=[
                ", ".join(c['meanings']),
                c['word'] if c['word'] is not None else "",
                #c['image_filename'] if c['image_filename'] is not None else '',
                c['meaning_mnemonic'],
                f'{full_name}::{", ".join(c["meanings"])}',
                c['wanikani_level'],
                #c['Tags'],
            ],
        )
        anki_deck.add_note(note)
    return anki_deck

def export_to_anki(decks: List, images: List):
    anki_model_radicals = genanki.Model(
        1561628560,
        'Genkikani Model - Radicals',
        fields=[
            {'name': 'meanings'},
            {'name': 'word'},
            #{'name': 'image'},
            {'name': 'meaning_mnemonic'},
            {'name': 'uuid'},
            {'name': 'wanikani_level'},
            #{'name': 'Tags'},
        ],
        templates=[{
            'name': 'Recognition',
            'qfmt': radical_frontside,
            'afmt': radical_backside,
        }],
        css=styling
    )
    anki_model_kanjis = genanki.Model(
        1561628561,
        'Genkikani Model - Kanji',
            fields=[
                {'name': 'meanings'},
                {'name': 'word'},
                {'name': 'readings_on'},
                {'name': 'readings_kun'},
                {'name': 'meaning_mnemonic'},
                {'name': 'meaning_hint'},
                {'name': 'reading_mnemonic'},
                {'name': 'reading_hint'},
                {'name': 'radicals'},# todo: fix color of wanikani radicals
                {'name': 'radicals_names'},
                {'name': 'similar_kanji'},
                {'name': 'similar_kanji_names'},
                {'name': 'uuid'},
                {'name': 'genki_lesson_num'},
                {'name': 'wanikani_level'},
                {'name': 'KKLC'},
                {'name': 'KKLD_2ed'},
                {'name': 'frequency'},
                {'name': 'strokes'},
                {'name': 'grade'},
                {'name': 'jlpt'},
                {'name': 'KKLD_SKIP_code'},
                #{'name': 'Tags'},
            ],
        templates=[{
            'name': 'Recognition',
            'qfmt': kanji_frontside,
            'afmt': kanji_backside,
        }],
        css=styling
    )
    anki_model_vocabulary = genanki.Model(
        1561628562,
        'Genkikani Model - Vocabulary',
        fields=[
            {'name': 'meanings'},
            {'name': 'word'},
            {'name': 'readings'},
            {'name': 'meaning_mnemonic'},
            {'name': 'reading_mnemonic'},
            {'name': 'kanjis'},
            {'name': 'kanjis_names'},
            {'name': 'type'},
            {'name': 'sentences'},
            {'name': 'note'},
            {'name': 'full_kanji'},
            {'name': 'sound'},
            {'name': 'uuid'},
            {'name': 'genki_lesson_num'},
            {'name': 'wanikani_level'},
            #{'name': 'Tags'},
        ],
        templates=[
            {
                'name': 'Recognition',
                'qfmt': vocab_frontside,
                'afmt': vocab_backside,
            },
            {
                'name': 'Reading',
                'qfmt': vocab_reading_frontside,
                'afmt': vocab_reading_backside,
            },
        ],
        css=styling
    )
    anki_model_kana_vocabulary = genanki.Model(
        1561628563,
        'Genkikani Model - Kana Vocabulary',
        fields=[
            {'name': 'meanings'},
            {'name': 'word'},
            {'name': 'meaning_mnemonic'},
            {'name': 'type'},
            {'name': 'sentences'},
            {'name': 'note'},
            {'name': 'sound'},
            {'name': 'uuid'},
            {'name': 'genki_lesson_num'},
            {'name': 'wanikani_level'},
            #{'name': 'Tags'},
        ],
        templates=[
            {
                'name': 'Recognition',
                'qfmt': kana_vocab_frontside,
                'afmt': kana_vocab_backside,
            }
        ],
        css=styling
    )

    anki_decks = []
    sound_files = []
    start_uuid = 284760580
    image_files = images
    deck_name = "GenkiKani"
    for i, lection in enumerate(decks):

        # radicals
        if 'radicals' in lection:
            radical_deck = gen_radical_deck(lection['radicals'], f'{deck_name}::{lection["name"]}::0 Radicals', anki_model_radicals, start_uuid + i*10)
            anki_decks.append(radical_deck)

        # kanjis
        if 'kanjis' in lection:
            kanji_deck = gen_kanji_deck(lection['kanjis'], f'{deck_name}::{lection["name"]}::1 Kanji', anki_model_kanjis, start_uuid + i*10 + 1)
            anki_decks.append(kanji_deck)

        # vocabulary important
        if 'vocabulary_important' in lection:
            vocab_deck_important = gen_vocab_deck(lection['vocabulary_important'], f'{deck_name}::{lection["name"]}::2 Vocabulary', anki_model_vocabulary, start_uuid + i*10 + 2, sound_files)
            anki_decks.append(vocab_deck_important)

        # vocabulary WaniKani
        if 'vocabulary_wanikani' in lection:
            vocab_deck_additional = gen_vocab_deck(lection['vocabulary_wanikani'], f'{deck_name}::{lection["name"]}::3 Additional Vocabulary (WK)', anki_model_vocabulary, start_uuid + i*10 + 3, sound_files)
            anki_decks.append(vocab_deck_additional)

        # vocabulary unimportant
        if 'vocabulary_unimportant' in lection:
            vocab_deck_unimportant = gen_vocab_deck(lection['vocabulary_unimportant'], f'{deck_name}::{lection["name"]}::4 Unimportant Vocabulary', anki_model_vocabulary, start_uuid + i*10 + 4, sound_files)
            anki_decks.append(vocab_deck_unimportant)

        # Remaining WK vocabulary
        if 'vocabulary' in lection:
            vocab_deck = gen_vocab_deck(lection['vocabulary'], f'{deck_name}::{lection["name"]}::5 Remaining WK Vocabulary', anki_model_vocabulary, start_uuid + i*10 + 5, sound_files)
            anki_decks.append(vocab_deck)

        # WK kana vocabulary
        if 'kana_vocabulary' in lection:
            kana_vocab_deck = gen_kana_vocab_deck(lection['kana_vocabulary'], f'{deck_name}::{lection["name"]}::6 Kana Vocabulary', anki_model_kana_vocabulary, start_uuid + i*10 + 6, sound_files)
            anki_decks.append(kana_vocab_deck)

        # hidden radicals
        if 'radicals_hidden' in lection:
            radical_hidden_deck = gen_radical_deck(lection['radicals_hidden'], f'{deck_name}::{lection["name"]}::7 Hidden Radicals', anki_model_radicals, start_uuid + i*10 + 7)
            anki_decks.append(radical_hidden_deck)

        # hidden kanjis
        if 'kanjis_hidden' in lection:
            kanji_hidden_deck = gen_kanji_deck(lection['kanjis_hidden'], f'{deck_name}::{lection["name"]}::8 Hidden Kanji', anki_model_kanjis, start_uuid + i*10 + 8)
            anki_decks.append(kanji_hidden_deck)

        # hidden vocabulary
        if 'vocabulary_hidden' in lection:
            vocabulary_hidden_deck = gen_vocab_deck(lection['vocabulary_hidden'], f'{deck_name}::{lection["name"]}::9 Hidden Vocabulary', anki_model_vocabulary, start_uuid + i*10 + 9, sound_files)
            anki_decks.append(vocabulary_hidden_deck)

        # hidden kana vocabulary
        # As of 2026-02-27, there are no hidden kana vocabulary.
        if 'kana_vocabulary_hidden' in lection:
            # 200,000 should be enough to avoid number collision.
            kana_vocabulary_hidden_deck = gen_vocab_deck(lection['kana_vocabulary_hidden'], f'{deck_name}::{lection["name"]}::10 Hidden Kana Vocabulary', anki_model_kana_vocabulary, start_uuid + 200000 + i*10, sound_files)
            anki_decks.append(kana_vocabulary_hidden_deck)

    anki_package = genanki.Package(anki_decks)

    media_files = [f'data/wanikani/images/{image}' for image in image_files]
    #print(f'media files: {media_files}')
    media_files.extend([f'data/wanikani/sound/{sound}' for sound in sound_files])

    # font
    media_files.append("data/fonts/_hirakakyprow3.otf")

    anki_package.media_files = media_files

    #anki_package.write_to_file('wanigenki.apkg')
    anki_package.write_to_file('genkikani.apkg')
