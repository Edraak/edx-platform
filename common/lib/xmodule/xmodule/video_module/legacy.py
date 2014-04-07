def download_youtube_subs_and_generate_for_all_speeds(youtube_subs, item, settings):
    """
    Download transcripts from Youtube and save them to assets.

    Args:
    youtube_subs: dictionary of `speed: youtube_id` key:value pairs.
    item: video module instance.

    Returns: None, if transcripts were successfully downloaded and saved.
    Otherwise raises GetTranscriptsFromYouTubeException.
    """
    i18n = item.runtime.service(item, "i18n")
    _ = i18n.ugettext

    highest_speed = highest_speed_subs = None
    missed_speeds = []
    # Iterate from lowest to highest speed and try to do download transcripts
    # from the Youtube service.
    for speed, youtube_id in sorted(youtube_subs.iteritems()):
        if not youtube_id:
            continue
        try:
            subs = get_transcripts_from_youtube(youtube_id, settings, i18n)
            if not subs:  # if empty subs are returned
                raise GetTranscriptsFromYouTubeException
        except GetTranscriptsFromYouTubeException:
            missed_speeds.append(speed)
            continue

        save_subs_to_store(subs, youtube_id, item)

        log.info(
            "Transcripts for YouTube id %s (speed %s)"
            "are downloaded and saved.", youtube_id, speed
        )

        highest_speed = speed
        highest_speed_subs = subs

    if not highest_speed:
        raise GetTranscriptsFromYouTubeException(_("Can't find any transcripts on the Youtube service."))

    # When we exit from the previous loop, `highest_speed` and `highest_speed_subs`
    # are the transcripts data for the highest speed available on the
    # Youtube service. We use the highest speed as main speed for the
    # generation other transcripts, cause during calculation timestamps
    # for lower speeds we just use multiplication instead of division.
    for speed in missed_speeds:  # Generate transcripts for missed speeds.
        save_subs_to_store(
            generate_subs(speed, highest_speed, highest_speed_subs),
            youtube_subs[speed],
            item
        )

        log.info(
            "Transcripts for YouTube id %s (speed %s)"
            "are generated from YouTube id %s (speed %s) and saved",
            youtube_subs[speed], speed,
            youtube_subs[highest_speed],
            highest_speed
        )
