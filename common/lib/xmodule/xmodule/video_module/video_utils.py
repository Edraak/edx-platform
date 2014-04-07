"""
Module containts utils specific for video_module.
"""


def create_youtube_string(video):
    """
    Create a string of Youtube IDs from `module`'s metadata
    attributes. Only writes a speed if an ID is present in the
    module.  Necessary for backwards compatibility with XML-based
    courses.
    """
    youtube_ids = [
        video.youtube_id_0_75,
        video.youtube_id_1_0,
        video.youtube_id_1_25,
        video.youtube_id_1_5
    ]
    youtube_speeds = ['0.75', '1.00', '1.25', '1.50']
    return ','.join([
        ':'.join(pair)
        for pair
        in zip(youtube_speeds, youtube_ids)
        if pair[1]
    ])


def youtube_speed_dict(video):
    """
    Returns {speed: youtube_ids, ...} dict for existing youtube_ids
    """
    yt_ids = [
        video.youtube_id_0_75,
        video.youtube_id_1_0,
        video.youtube_id_1_25,
        self.descriptor.youtube_id_1_5
    ]
    yt_speeds = [0.75, 1.00, 1.25, 1.50]
    youtube_ids = {p[0]: p[1] for p in zip(yt_ids, yt_speeds) if p[0]}
    return youtube_ids


def get_html5_ids(html5_sources):
    """
    Helper method to parse out an HTML5 source into the ideas
    NOTE: This assumes that '/' are not in the filename

    Args:
        httml5_sources: list of strings.
    """
    html5_ids = [x.split('/')[-1].rsplit('.', 1)[0] for x in html5_sources]
    return html5_ids
