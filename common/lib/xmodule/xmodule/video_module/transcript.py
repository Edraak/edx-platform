class Srt(AbstractClass):
    MIME_TYPE = 'application/x-subrip'

    @staticmethod
    def get(contestore, location, filename):
        name = Srt.get_filename(filename)

    @staticmethod
    def add(contestore, location, filename):
        name = Srt.get_filename(filename)

    @staticmethod
    def delete(contestore, location, filename):
        name = Srt.get_filename(filename)

    @staticmethod
    def copy(contestore, location, filename):
        name = Srt.get_filename(filename)

    @staticmethod
    def rename(contestore, location, filename):
        name = Srt.get_filename(filename)

    @staticmethod
    def get_filename(contestore, location, filename):
        pass

    @staticmethod
    def get_mime_type():
        return Srt.MIME_TYPE


class Transcript(object):
    """
    Container for transcript methods.
    """

    mime_types = {
        'srt': 'application/x-subrip; charset=utf-8',
        'txt': 'text/plain; charset=utf-8',
        'sjson': 'application/json',
    }

    class TranscriptException(Exception):
        """
        When ?
        """
        pass


    class TranscriptsGenerationException(Exception):
        """
        When ?
        """
        pass


    class GetTranscriptsFromYouTubeException(Exception):
        """
        When ?
        """
        pass


    class TranscriptsRequestValidationException(Exception):
        """
        When ?
        """
        pass



    def __init__ (video_descriptor_instance):
        self.descriptor = video_descriptor_instance
        self.location = video_descriptor_instance.location


    @staticmethod
    def subs_filename(subs_id, lang='en'):
    """
    Generate proper filename for storage.
    """
    if lang == 'en':
        return u'subs_{0}.srt.sjson'.format(subs_id)
    else:
        return u'{0}_subs_{1}.srt.sjson'.format(lang, subs_id)


    @staticmethod
    def convert(content, input_format, output_format):
        """
        Convert transcript `content` from `input_format` to `output_format`.

        Accepted input formats: sjson, srt.
        Accepted output format: srt, txt.
        """
        assert input_format in ('srt', 'sjson')
        assert output_format in ('txt', 'srt', 'sjson')

        if input_format == output_format:
            return content

        if input_format == 'srt':

            if output_format == 'txt':
                text = SubRipFile.from_string(content.decode('utf8')).text
                return HTMLParser().unescape(text)

            elif output_format == 'sjson':
                raise NotImplementedError

        if input_format == 'sjson':

            if output_format == 'txt':
                text = json.loads(content)['text']
                return HTMLParser().unescape("\n".join(text))

            elif output_format == 'srt':
                return generate_srt_from_sjson(json.loads(content), speed=1.0)

    @staticmethod
    def change_sjson_subs_speed(to_speed, from_speed, sjson_subs):
    """
    Generate transcripts from one speed to another speed.

    Args:
    `to_speed`: float, for this speed subtitles will be generated,
    `from_speed`: float, speed of source_subs
    `sjson_subs`: dict, existing subtitles for speed `source_speed`.

    Returns:
    `subs`: dict, actual subtitles.
    """
    if to_speed == from_speed:
        return sjson_subs

    coefficient = 1.0 * to_speed / from_speed
    subs = {
        'start': [
            int(round(timestamp * coefficient)) for
            timestamp in sjson_subs['start']
        ],
        'end': [
            int(round(timestamp * coefficient)) for
            timestamp in sjson_subs['end']
        ],
        'text': sjson_subs['text']}
    return subs


    def get_asset_by_filename(filename):
        """
        Return asset by location and filename.
        """
        return contentstore().find(self.asset_location(filename))

    def get_asset_by_subsid(self, subs_id, lang='en'):
        """
        Get asset from contentstore, asset location is built from subs_id and lang.
        """
        asset_filename = subs_filename(subs_id, lang)
        return self.get_asset_by_filename(self.location, asset_filename)

    def asset_location(self, filename):
        """
        Return asset location.
        """
        return StaticContent.compute_location(self.location.org, self.location.course, filename)

    def delete_asset(self, filename):
        """
        Delete asset by location and filename.
        """
        try:
            content = self.get_asset(filename)
            contentstore().delete(content.get_id())
            log.info("Transcript asset %s was removed from store.", filename)
        except NotFoundError:
            pass

    def delete_asset_by_subsid(self, subs_id, lang='en'):
        """
        Remove from store, if transcripts content exists.
        """
        filename = self.subs_filename(subs_id, lang)
        self.delete_asset(item.location, filename)


    def save_asset(content, content_name, mime_type):
    """
    Save named content to store. Returns location of saved content.
    """
    content_location = self.asset_location(content_name)
    content = StaticContent(content_location, content_name, mime_type, content)
    contentstore().save(content)
    return content_location


    def save_sjson_asset(sjson_content, subs_id, language='en'):
        """
        Save transcripts into `StaticContent`.

        Args:
        `subs_id`: str, subtitles id
        `language`: two chars str ('uk'), language of translation of transcripts

        Returns: location of saved subtitles.
        """
        filedata = json.dumps(sjson_content, indent=2)
        filename = self.subs_filename(subs_id, language)
        return self.save_asset(filedata, filename, 'application/json')

    # def get (self, className, filename):
    #     return className.get(contentstore, self.location, filename)

    # def set (self, className):
    #     className.get(contentstore);

    # def delete (self, className):
    #     className.get();


