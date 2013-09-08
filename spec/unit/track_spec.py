# -*- coding: utf-8 -*-

from spec.unit.fixtures import Internal, patch_gpod_module

patch_gpod_module()

from ipodio.track import Track

from expects import expect
from mockito import mock, spy, when, verify, any
from mamba import describe, context, before


with describe(Track) as _:

    with context('when fabricated'):
        def should_have_an_internal_track():
            expect(_.fabricated_track.internal).to.be.an(_.internal_class)

    with context('when constructed'):
        def should_have_an_internal_track_():
            expect(_.track.internal).to.be.an(_.internal_class)

        def should_set_hash_to_none():
            expect(_.track.hash).to.be(None)

    with context('when update_hash'):
        def should_compute_hash():
            track = spy(_.track)

            track.update_hash()

            verify(_.track._hasher).hash('filename.mp3')

    with context('when compute_hash'):
        def should_use_the_hasher():
            _.track.compute_hash()

            verify(_.track._hasher).hash('filename.mp3')

        def should_return_the_hash_when_computed():
            expect(_.track.compute_hash()).to.be(_.hash)

    def should_save_hash_when_set():
        _.track.hash = _.hash

        expect(_.track.hash).to.be(_.hash)

    with context('the number property'):
        def should_be_an_integer():
            expect(_.track.number).to.be.an(int)

        def should_be_none_if_unset():
            track = create_track(track_nr=None)

            expect(track.number).to.be.none

    with context('the title property'):
        def should_be_unicode():
            expect(_.track.title).to.be.an(unicode)

        def should_never_be_none_but_empty_instead():
            track = create_track(title=None)

            expect(track.title).to.be.equal(u'')

    with context('the album property'):
        def should_be_unicode_():
            expect(_.track.album).to.be.an(unicode)

        def should_never_be_none_but_empty_instead_():
            track = create_track(album=None)

            expect(track.album).to.be.equal(u'')

    with context('the artist property'):
        def should_be_unicode__():
            expect(_.track.artist).to.be.an(unicode)

        def should_never_be_none_but_empty_instead__():
            track = create_track(artist=None)

            expect(track.artist).to.be.equal(u'')

    with context('the extension property'):
        def should_be_unicode___():
            expect(_.track.extension).to.be.an(unicode)

        def should_be_mp3_if_filetype_is_MPEG():
            track = create_track(filetype='MPEG audio file')

            expect(track.extension).to.be.equal(u'mp3')

        def should_be_mp3_if_filetype_is_none_but_file_path_ends_in_mp3():
            track = create_track(filetype=None, filename_locale='/path/file.mp3')

            expect(track.extension).to.be.equal(u'mp3')

        def should_be_m4a_if_filetype_is_AAC():
            track = create_track(filetype='AAC audio file')

            expect(track.extension).to.be.equal(u'm4a')

        def should_be_m4a_if_filetype_is_none_but_file_path_ends_in_m4a():
            track = create_track(filetype=None, filename_locale='/path/file.m4a')

            expect(track.extension).to.be.equal(u'm4a')

        def should_be_aiff_if_filetype_is_AIFF():
            track = create_track(filetype='AIFF audio file')

            expect(track.extension).to.be.equal(u'aiff')

        def should_be_aiff_if_filetype_is_none_but_file_path_ends_in_aiff():
            track = create_track(filetype=None, filename_locale='/path/file.aiff')

            expect(track.extension).to.be.equal(u'aiff')

    with context('the filename_from_tags property'):
        def should_be_a_composed_name_from_track_tag_info():
            expect(_.track.filename_from_tags).to.be.equal(
                '2_The_Title__The_Artist.mp3')

        def should_be_an_almost_ISO9660_compliant_filename():
            almost_iso9660 = r'^\w+\.\w+$'

            expect(_.track.filename_from_tags).to.match(almost_iso9660)

    with context('when printed'):
        def should_output_track_attributes():
            expect(str(_.track)).to.be.equal("2. 'The Title' by: 'The Artist'")

    @before.each
    def fixture():
        _.internal_class = Internal
        _.hash = '204939024023840234'

        _.hasher = mock()
        when(_.hasher).hash(any(unicode)).thenReturn(_.hash)

        _.track_data = {
            'userdata': {},
            'track_nr': 2,
            'title': 'The Title',
            'album': None,
            'artist': 'The Artist'
        }
        _.track = Track(Internal(_.track_data), hasher=_.hasher)
        _.fabricated_track = Track.create(
            _.track_data, internal_class=_.internal_class)

    def create_track(**kwargs):
        data = dict(_.track_data)
        data.update(kwargs)
        return Track.create(data, internal_class=_.internal_class)
