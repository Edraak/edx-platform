"""
Utility functions for transcripts.
++++++++++++++++++++++++++++++++++
"""
import os
import copy
import json
import requests
import logging
from pysrt import SubRipTime, SubRipItem, SubRipFile
from lxml import etree
from HTMLParser import HTMLParser

from xmodule.exceptions import NotFoundError
from xmodule.contentstore.content import StaticContent
from xmodule.contentstore.django import contentstore


log = logging.getLogger(__name__)


def get_transcripts_from_youtube(youtube_id, settings, i18n):
    """
    Gets transcripts from youtube for youtube_id.

    Parses only UTF8 encoded transcripts.

    Returns (status, transcripts): bool, dict.
    """
    _ = i18n.ugettext

    utf8_parser = etree.XMLParser(encoding='utf-8')

    youtube_text_api = copy.deepcopy(settings.YOUTUBE['TEXT_API'])
    youtube_text_api['params']['v'] = youtube_id
    data = requests.get('http://' + youtube_text_api['url'], params=youtube_text_api['params'])

    if data.status_code != 200 or not data.text:
        msg = _("Can't receive transcripts from Youtube for {youtube_id}. Status code: {status_code}.").format(
            youtube_id=youtube_id,
            status_code=data.status_code
        )
        raise GetTranscriptsFromYouTubeException(msg)

    sub_starts, sub_ends, sub_texts = [], [], []
    xmltree = etree.fromstring(data.content, parser=utf8_parser)
    for element in xmltree:
        if element.tag == "text":
            start = float(element.get("start"))
            duration = float(element.get("dur", 0))  # dur is not mandatory
            text = element.text
            end = start + duration

            if text:
                # Start and end should be ints representing the millisecond timestamp.
                sub_starts.append(int(start * 1000))
                sub_ends.append(int((end + 0.0001) * 1000))
                sub_texts.append(text.replace('\n', ' '))

    return {'start': sub_starts, 'end': sub_ends, 'text': sub_texts}


def download_youtube_subs(youtube_id, item, settings):
    """
    Download transcripts from Youtube and save them to assets.

    Args:
    youtube_id: youtube_id to download
    item: video module instance.

    Returns: None, if transcripts were successfully downloaded and saved.
    Otherwise raises GetTranscriptsFromYouTubeException.
    """
    i18n = item.runtime.service(item, "i18n")
    _ = i18n.ugettext
    subs = get_transcripts_from_youtube(youtube_id, settings, i18n)
    save_subs_to_store(subs, youtube_id, item)
    log.info("Transcripts for YouTube id %s for 1.0 speed are downloaded and saved.", youtube_id)


def generate_subs_from_source(speed_subs, subs_type, subs_filedata, item, language='en'):
    """Generate transcripts from source files (like SubRip format, etc.)
    and save them to assets for `item` module.
    We expect, that speed of source subs equal to 1

    :param speed_subs: dictionary {speed: sub_id, ...}
    :param subs_type: type of source subs: "srt", ...
    :param subs_filedata:unicode, content of source subs.
    :param item: module object.
    :param language: str, language of translation of transcripts
    :returns: True, if all subs are generated and saved successfully.
    """
    _ = item.runtime.service(item, "i18n").ugettext
    if subs_type.lower() != 'srt':
        raise TranscriptsGenerationException(_("We support only SubRip (*.srt) transcripts format."))
    try:
        srt_subs_obj = SubRipFile.from_string(subs_filedata)
    except Exception as ex:
        msg = _("Something wrong with SubRip transcripts file during parsing. Inner message is {error_message}").format(
            error_message=ex.message
        )
        raise TranscriptsGenerationException(msg)
    if not srt_subs_obj:
        raise TranscriptsGenerationException(_("Something wrong with SubRip transcripts file during parsing."))

    sub_starts = []
    sub_ends = []
    sub_texts = []

    for sub in srt_subs_obj:
        sub_starts.append(sub.start.ordinal)
        sub_ends.append(sub.end.ordinal)
        sub_texts.append(sub.text.replace('\n', ' '))

    subs = {
        'start': sub_starts,
        'end': sub_ends,
        'text': sub_texts}

    for speed, subs_id in speed_subs.iteritems():
        save_subs_to_store(
            generate_subs(speed, 1, subs),
            subs_id,
            item,
            language
        )

    return subs


def generate_srt_from_sjson(sjson_subs, speed):
    """Generate transcripts with speed = 1.0 from sjson to SubRip (*.srt).

    :param sjson_subs: "sjson" subs.
    :param speed: speed of `sjson_subs`.
    :returns: "srt" subs.
    """

    output = ''

    equal_len = len(sjson_subs['start']) == len(sjson_subs['end']) == len(sjson_subs['text'])
    if not equal_len:
        return output

    sjson_speed_1 = generate_subs(speed, 1, sjson_subs)

    for i in range(len(sjson_speed_1['start'])):
        item = SubRipItem(
            index=i,
            start=SubRipTime(milliseconds=sjson_speed_1['start'][i]),
            end=SubRipTime(milliseconds=sjson_speed_1['end'][i]),
            text=sjson_speed_1['text'][i]
        )
        output += (unicode(item))
        output += '\n'
    return output


def copy_or_rename_transcript(new_name, old_name, item, delete_old=False, user=None):
    """
    Renames `old_name` transcript file in storage to `new_name`.

    If `old_name` is not found in storage, raises `NotFoundError`.
    If `delete_old` is True, removes `old_name` files from storage.
    """
    filename = 'subs_{0}.srt.sjson'.format(old_name)
    content_location = StaticContent.compute_location(
        item.location.org, item.location.course, filename
    )
    transcripts = contentstore().find(content_location).data
    save_subs_to_store(json.loads(transcripts), new_name, item)
    item.sub = new_name
    item.save_with_metadata(user)
    if delete_old:
        remove_subs_from_store(old_name, item)



def manage_video_subtitles_save(item, user, old_metadata=None, generate_translation=False):
    """
    Does some specific things, that can be done only on save.

    Video player item has some video fields: HTML5 ones and Youtube one.

    If value of `sub` field of `new_item` is cleared, transcripts should be removed.

    `item` is video module instance with updated values of fields,
    but actually have not been saved to store yet.

    `old_metadata` contains old values of XFields.

    # 1.
    If value of `sub` field of `new_item` is different from values of video fields of `new_item`,
    and `new_item.sub` file is present, then code in this function creates copies of
    `new_item.sub` file with new names. That names are equal to values of video fields of `new_item`
    After that `sub` field of `new_item` is changed to one of values of video fields.
    This whole action ensures that after user changes video fields, proper `sub` files, corresponding
    to new values of video fields, will be presented in system.

    # 2 convert /static/filename.srt  to filename.srt in self.transcripts.
    (it is done to allow user to enter both /static/filename.srt and filename.srt)

    # 3. Generate transcripts translation only  when user clicks `save` button, not while switching tabs.
    a) delete sjson translation for those languages, which were removed from `item.transcripts`.
        Note: we are not deleting old SRT files to give user more flexibility.
    b) For all SRT files in`item.transcripts` regenerate new SJSON files.
        (To avoid confusing situation if you attempt to correct a translation by uploading
        a new version of the SRT file with same name).
    """

    _ = item.runtime.service(item, "i18n").ugettext

    # 1.
    html5_ids = get_html5_ids(item.html5_sources)
    possible_video_id_list = [item.youtube_id_1_0] + html5_ids
    sub_name = item.sub
    for video_id in possible_video_id_list:
        if not video_id:
            continue
        if not sub_name:
            remove_subs_from_store(video_id, item)
            continue
        # copy_or_rename_transcript changes item.sub of module
        try:
            # updates item.sub with `video_id`, if it is successful.
            copy_or_rename_transcript(video_id, sub_name, item, user=user)
        except NotFoundError:
            # subtitles file `sub_name` is not presented in the system. Nothing to copy or rename.
            log.debug(
                "Copying %s file content to %s name is failed, "
                "original file does not exist.",
                sub_name, video_id
            )

    # 2.
    if generate_translation:
        for lang, filename in item.transcripts.items():
            item.transcripts[lang] = os.path.split(filename)[-1]

    # 3.
    if generate_translation:
        old_langs = set(old_metadata.get('transcripts', {})) if old_metadata else set()
        new_langs = set(item.transcripts)

        for lang in old_langs.difference(new_langs):  # 3a
            for video_id in possible_video_id_list:
                if video_id:
                    remove_subs_from_store(video_id, item, lang)

        reraised_message = ''
        for lang in new_langs:  # 3b
            try:
                generate_sjson_for_all_speeds(
                    item,
                    item.transcripts[lang],
                    {speed: subs_id for subs_id, speed in youtube_speed_dict(item).iteritems()},
                    lang,
                )
            except TranscriptException as ex:
                item.transcripts.pop(lang)  # remove key from transcripts because proper srt file does not exist in assets.
                reraised_message += ' ' + ex.message
        if reraised_message:
            item.save_with_metadata(user)
            raise TranscriptException(reraised_message)


def generate_sjson_for_all_speeds(item, user_filename, result_subs_dict, lang):
    """
    Generates sjson from srt for given lang.

    `item` is module object.
    """
    _ = item.runtime.service(item, "i18n").ugettext

    try:
        srt_transcripts = contentstore().find(Transcript.asset_location(item.location, user_filename))
    except NotFoundError as ex:
        raise TranscriptException(_("{exception_message}: Can't find uploaded transcripts: {user_filename}").format(
            exception_message=ex.message,
            user_filename=user_filename
        ))

    if not lang:
        lang = item.transcript_language

    generate_subs_from_source(
        result_subs_dict,
        os.path.splitext(user_filename)[1][1:],
        srt_transcripts.data.decode('utf8'),
        item,
        lang
    )


def get_or_create_sjson(item):
    """
    Get sjson if already exists, otherwise generate it.

    Generate sjson with subs_id name, from user uploaded srt.
    Subs_id is extracted from srt filename, which was set by user.

    Raises:
        TranscriptException: when srt subtitles do not exist,
        and exceptions from generate_subs_from_source.

    `item` is module object.
    """
    user_filename = item.transcripts[item.transcript_language]
    user_subs_id = os.path.splitext(user_filename)[0]
    source_subs_id, result_subs_dict = user_subs_id, {1.0: user_subs_id}
    try:
        sjson_transcript = Transcript.asset(item.location, source_subs_id, item.transcript_language).data
    except (NotFoundError):  # generating sjson from srt
        generate_sjson_for_all_speeds(item, user_filename, result_subs_dict, item.transcript_language)
    sjson_transcript = Transcript.asset(item.location, source_subs_id, item.transcript_language).data
    return sjson_transcript

