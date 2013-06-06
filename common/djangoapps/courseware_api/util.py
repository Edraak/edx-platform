"""
Utilities
"""


def descendants(blocks, root):
    """
    Return a list of all the descendents of the start node (not including itself),
    in depth first order.
    """
    result = []

    def add_dfs(node_id):
        """Append all the descendants to list"""
        for child in blocks[node_id]['children']:
            result.append(blocks[child])
            add_dfs(child)

    add_dfs(root)
    return result


def print_course(structure):
    blocks = structure['blocks']
    course = blocks[structure['root']]

    print "######## Course: {0} #######".format(course['metadata']['display_name'])
    for section_id in course['children']:
        section = blocks[section_id]
        if section['category'] != 'chapter':
            continue

        print "# Section:" + section['metadata']['display_name']
        for subsection_id in section['children']:
            subsection = blocks[subsection_id]
            print "## Subsection:" + subsection['metadata']['display_name']
            for child in descendants(blocks, subsection_id):
                if child['category'] == 'video':
                    print "    VIDEO: " + child['metadata']['display_name']
                else:
                    print "    {0}: {1}".format(child['category'],
                                            child['metadata']['display_name'])



def main():
    course = {
            'id': 'edX/Welding/Power_Welding',
            'root': 'i4x://edX/Welding/course/Power_Welding',
            'blocks': {
                'i4x://edX/Welding/course/Power_Welding': {'category': 'course',
                    'children': ['i4x://edX/Welding/chapter/Welcome_to_Welding'],
                    'metadata': {'display_name': 'Power Welding'},
                    'definition': 'i4x://edX/Welding/course/Power_Welding',
                    },
                'i4x://edX/Welding/chapter/Welcome_to_Welding': {'category': 'chapter',
                    'children': ['i4x://edX/Welding/sequential/Your_first_weld'],
                    'metadata': {'display_name': 'Welcome to Welding'},
                    'definition': 'i4x://edX/Welding/chapter/Welcome_to_Welding',
                    },
                'i4x://edX/Welding/sequential/Your_first_weld': {'category': 'sequential',
                    'children': ['i4x://edX/Welding/vertical/random_hex'],
                    'metadata': {'display_name': 'Your first weld'},
                    'definition': 'i4x://edX/Welding/sequential/Your_first_weld',
                    },
                'i4x://edX/Welding/vertical/random_hex': {'category': 'vertical',
                    'children': ['i4x://edX/Welding/video/See_Fred_Weld',
                                 'i4x://edX/Welding/html/About_Welding',
                                 'i4x://edX/Welding/problem/Weld_This'],
                    'metadata': {'display_name': 'random hex'},
                    'definition': 'i4x://edX/Welding/vertical/random_hex',
                    },
                'i4x://edX/Welding/video/See_Fred_Weld': {'category': 'video',
                    'children': [],
                    'metadata': {'display_name': 'See Fred Weld'},
                    'definition': 'i4x://edX/Welding/video/See_Fred_Weld',
                    },
                'i4x://edX/Welding/html/About_Welding': {'category': 'html',
                    'metadata': {'display_name': 'About Welding'},
                    'children': [],
                    'definition': 'i4x://edX/Welding/html/About_Welding',
                    },
                'i4x://edX/Welding/problem/Weld_This': {'category': 'problem',
'metadata': {'display_name': 'Weld This'},
                    'children': [],
                    'definition': 'i4x://edX/Welding/problem/Weld_This',
                    }
                }
            }

    print_course(course)

if __name__ == "__main__":
    main()
