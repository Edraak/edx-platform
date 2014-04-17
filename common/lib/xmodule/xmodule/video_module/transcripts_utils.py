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
        raise Transcript.GetTranscriptFromYouTubeEx(msg)

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
    item.Transcript.save_sjson_asset(subs, youtube_id)
    log.info("Transcripts for YouTube id %s for 1.0 speed are downloaded and saved.", youtube_id)


def copy_or_rename_transcript(new_name, old_name, item, delete_old=False, user=None):
    """
    Renames `old_name` transcript file in storage to `new_name`.

    If `old_name` is not found in storage, raises `NotFoundError`.
    If `delete_old` is True, removes `old_name` files from storage.
    """
    transcripts = item.Transcript.get_asset_by_subsid(old_name).data
    item.Transcript.save_sjson_asset(json.loads(transcripts), new_name)
    item.sub = new_name
    item.save_with_metadata(user)
    if delete_old:
        item.Transcript.delete_asset_by_subsid(old_name)


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



