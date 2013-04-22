from django.test.client import Client

def test_profile():
    resp = get('/profile')
    parsed = {}
    self.assertEqual(parsed, {'name': 'Fred W',
                              'username': 'freddy',
                              'email': 'fred@edx.org',
                              'courses': [
                                  {'course_id': 'edX/Welding/2013',
                                   'name': 'Power Welding!',
                                   'description': 'This is Power Welding.',
                                   'image_url': 'https://www.edx.org/static/content-berkeley-cs191x~2013_Spring/images/course_image.jpg',
                                   'is_running': True}]})


def test_course():
    # Do not return stuff that isn't started

    expected_course = {
        'id': 'edX/Welding/2013',
        'blocks': {
            1: {'category': 'course',
                'children': [2],
                'metadata': {'display_name': 'Welding!'},
                'definition': 'i4x://edX/Welding/course/2013',
                },
            2: {'category': 'chapter',
                'children': [3],
                'metadata': {'display_name': 'Welcome to Welding'},
                'definition': 'i4x://edX/Welding/chapter/Welcome',
                },
            3: {'category': 'sequential',
                'children': [4],
                'metadata': {'display_name': 'Your first weld'},
                'definition': 'i4x://edX/Welding/sequential/your_first_weld',
                },
            4: {'category': 'vertical',
                'children': [5,6,7],
                'metadata': {'display_name': 'random hex'},
                'definition': 'i4x://edX/Welding/vertical/deadbeef',
},
            5: {'category': 'video',
                'children': [],
                'metadata': {'display_name': 'See Fred Weld'},
                'definition': 'i4x://edX/Welding/video/see_fred_weld',
},
            6: {'category': 'html',
                'metadata': {'display_name': 'About Welding'},
                'children': [],
                'definition': 'i4x://edX/Welding/html/about_welding',
}
            7: {'category': 'problem',
                'metadata': {'display_name': 'Weld this'},
                'children': [],
                'definition': 'i4x://edX/Welding/problem/weld_this',
}
            }
        }
    self.assertEqual(parsed, expected_course)



def test_xblock_problem():
    expected = {
        'location': 'i4x://edX/Welding/problem/weld_this',
        'category': 'problem',
        'message': 'Problems not supported yet'
    # ???
    }


def test_xblock_sequential():
    expected = {
        'location': 'i4x://edX/Welding/sequential/your_first_weld',
        'category': 'sequential',
        'message': "Sequentials don't have any interesting definition"
    # ???
    }

def test_xblock_vertical():
    expected = {
        'location': 'i4x://edX/Welding/vertical/deadbeef',
        'category': 'vertical',
        'message': "Verticals don't have any interesting definition"
    # ???
    }


def test_xblock_video():
    expected = {
        'location': 'i4x://edX/Welding/video/see_fred_weld',
        'category': 'video',
        'youtube_id': 'abc123',
        'display_name': 'See Fred weld!'
        }


def test_xblock_html():
    expected = {
        'location': 'i4x://edX/Welding/html/about_welding',
        'category': 'html',
        'html': '''<div>Welding is cool.  We weld a lot at edX,
        while putting the pieces of our site together after our
        servers blow up.'''
        }

