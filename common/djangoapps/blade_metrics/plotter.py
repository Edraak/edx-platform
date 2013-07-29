from pymongo import MongoClient
import re
import collections
import matplotlib.pyplot as plt
import os.path
from itertools import chain
import bson


class MongoIndexer:

    def __init__(self, host='localhost', port=27017, content_database='xcontent', file_collection="fs.files",
                 chunk_collection="fs.chunks", module_database='xmodule', module_collection='modulestore'):
        self.host = host
        self.port = port
        self.client = MongoClient(host, port)
        self.content_db = self.client[content_database]
        self.module_db = self.client[module_database]
        try:
            self.content_db.collection_names().index(file_collection)
        except ValueError:
            print "No collection named: " + file_collection
            raise
        try:
            self.content_db.collection_names().index(chunk_collection)
        except ValueError:
            print "No collection named: " + chunk_collection
        self.file_collection = self.content_db[file_collection]
        self.chunk_collection = self.content_db[chunk_collection]
        self.module_collection = self.module_db[module_collection]

    def find_files_with_type(self, file_ending):
        """Returns a cursor for content files matching given type"""
        return self.file_collection.find({"filename": re.compile(".*?"+re.escape(file_ending))})

    def find_chunks_with_type(self, file_ending):
        """Returns a chunk cursor for content files matching given type"""
        return self.chunk_collection.find({"files_id.name": re.compile(".*?"+re.escape(file_ending))})

    def find_modules_by_category(self, category):
        """Returns a cursor for all xmodules matching given category"""
        return self.module_collection.find({"_id.category": category})

    def find_problems_by_tag(self, tag):
        """Returns a cursor that will iterate through all problems with the given tag"""
        query = {"_id.category": "problem", "definition.data": re.compile(".*?<"+tag+".*?")}
        return self.module_collection.find(query)

    def find_category_with_field(self, category, field):
        """Returns a cursor that iterates through all modules with the given category and something in given field"""
        query = {"_id.category": category, field: re.compile(".+")}
        return self.module_collection.find(query)

    def find_problems_by_tag_with_tag(self, problem, tag):
        pattern = re.compile(".*?<"+problem+".*?"+"<"+tag+".*?")
        query = {"_id.category": "problem",
                 "definition.data": pattern}
        return self.module_collection.find(query)

    def custom_query(self, query, collection="modulestore"):
        if "module" in collection.lower():
            return self.module_collection.find(query)
        elif "file" in collection.lower():
            return self.file_collection.find(query)
        elif "chunk" in collection.lower():
            return self.chunk_collection.find(query)


class Plotter:

    def __init__(self, content="xcontent", module="xmodule",
                 edge_content="edge-xcontent", edge_module="edge-xmodule"):
        self.prod_index = MongoIndexer(content_database=content, module_database=module)
        self.edge_index = MongoIndexer(content_database=edge_content, module_database=edge_module)

    def get_course_usage(self, cursor):
        get_course = lambda dao: dao["_id"]["course"]
        usage = []
        for i in range(0, cursor.count()):
            item = cursor.next()
            if isinstance(item["_id"], bson.objectid.ObjectId):
                continue
            else:
                usage.append(get_course(item))
        return collections.Counter(usage)

    def produce_graphs(self, category, bins, xlabel="Number of Appearances",
                       ylabel="Number of Courses", problem=False, **kwargs):
        """Produces relevant plots for modules of a given category for edge, prod, and both

        If problem is set to true then category becomes the xml tag being searched within the problem category"""
        if kwargs.get("queries", False):
            prod_cursor = self.prod_index.find_modules_by_category("fakeqwerty")  # empty generators
            edge_cursor = self.edge_index.find_modules_by_category("fakeqwerty")
            for k, v in kwargs["queries"].items():
                prod_function = getattr(self.prod_index, k)
                prod_cursor = chain(prod_cursor, prod_function(*v))
                edge_function = getattr(self.edge_index, k)
                edge_cursor = chain(edge_cursor, edge_function(*v))
        elif not problem:
            prod_cursor = self.prod_index.find_modules_by_category(category)
            edge_cursor = self.edge_index.find_modules_by_category(category)
        else:
            prod_cursor = self.prod_index.find_problems_by_tag(category)
            edge_cursor = self.edge_index.find_problems_by_tag(category)
        print prod_cursor.count()
        print edge_cursor.count()
        prod_usage = self.get_course_usage(prod_cursor)
        edge_usage = self.get_course_usage(edge_cursor)
        # If constrained bins are passed in, the top bin should hold everything above that limit as well
        if isinstance(bins, list):
            clipping = lambda value, bins: value if value <= bins[-1] else bins[-1]-1
            prod_values = [clipping(entry, bins) for entry in prod_usage.values()]
            edge_values = [clipping(entry, bins) for entry in edge_usage.values()]
        else:
            prod_values = prod_usage.values()
            edge_values = edge_usage.values()

        if prod_values:
            plt.clf()
            plt.hist(prod_values, bins=bins)
            plt.title(category + " on prod")
            print "Total courses on prod: " + str(len(prod_values))
            print "Total " + category + " on prod: " + str(sum(prod_usage.values()))
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)
            path = "graphs/"+category+"/prod.png"
            directory = os.path.dirname(path)
            if not os.path.exists(directory):
                os.makedirs(directory)
            plt.savefig(path)

        if edge_values:
            plt.clf()
            plt.hist(edge_values, bins=bins)
            plt.title(category + " on edge")
            print "Total courses on edge: " + str(len(edge_values))
            print "Total " + category + " on edge: " + str(sum(edge_usage.values()))
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)
            path = "graphs/"+category+"/edge.png"
            directory = os.path.dirname(path)
            if not os.path.exists(directory):
                os.makedirs(directory)
            plt.savefig(path)

        if prod_values and edge_values:
            plt.clf()
            plt.hist(prod_values+edge_values, bins=bins)
            plt.title(category + " overall")
            print "Total courses overall: " + str(len(prod_values)+len(edge_values))
            print "Total " + category + " overall: " + str(sum(prod_usage.values())+sum(edge_usage.values()))
            plt.xlabel(xlabel)
            path = "graphs/"+category+"/overall.png"
            directory = os.path.dirname(path)
            if not os.path.exists(directory):
                os.makedirs(directory)
            plt.savefig(path)

test = Plotter()
# test.produce_graphs("video", [5, 25, 45, 65, 85, 105])
# test.produce_graphs("discussion", [5, 25, 45, 65, 85, 105])
# test.produce_graphs("html", [5, 25, 45, 65, 85, 105])
# test.produce_graphs("poll_question", 5)
# test.produce_graphs("word_cloud", 5)
# test.produce_graphs("conditional", 5)
# test.produce_graphs("schematicresponse", 5, problem=True)
# test.produce_graphs("numericalresponse", [1, 6, 11, 16, 21, 26], problem=True)
# test.produce_graphs("multiplechoiceresponse", [1, 11, 21, 31, 41, 51, 61], problem=True)
# test.produce_graphs("stringresponse", [1, 6, 11, 16, 21, 26], problem=True)
# test.produce_graphs("formularesponse", [1, 6, 11, 16, 21, 26], problem=True)
# test.produce_graphs("imageresponse", 5, problem=True)
# test.produce_graphs("formularesponse", [1, 6, 11, 16, 21, 26], problem=True)
# test.produce_graphs("symbolicresponse", 5, problem=True)
# test.produce_graphs("chemicalequationinput", 5, problem=True)
# test.produce_graphs("annotationresponse", 5, problem=True)
# test.produce_graphs("optionresponse", 5, problem=True)
# test.produce_graphs("javascriptresponse", 5, problem=True)
# test.produce_graphs("choiceresponse", 5, problem=True)
# test.produce_graphs("truefalseresponse", 5, problem=True)
# test.produce_graphs("customresponse", 5, problem=True)
# test.produce_graphs("coderesponse", 5, problem=True)
# test.produce_graphs("externalresponse", 5, problem=True)
test.produce_graphs("latex", 5, queries={"find_category_with_field": ["html", "metadata.source_code"], "find_category_with_field": ["problem", "metadata.source_code"]})
