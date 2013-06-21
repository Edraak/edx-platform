Right now functionality is just at what is needed for present tasks, but should be easily modified for any further requests.

Right now within the plotter module there are two objects, MongoIndexer, and Plotter.
There are two different ways to use this module depending on how much flexibility you want.

For the most flexibility make your own MongoIndexer and use it to query for blades.
Example:

> from plotter import MongoIndexer
>
> mongo = MongoIndexer(host="localhost", port=27017, content_database="xcontent", module_database="xmodule")
> cursor = mongo.find_modules_by_category("video")
> cursor.next() # Returns dict representing mongo object

Alternately you can just have the prod, edge, and overall plots generated for you using the more involved Plotter object

Example:

> from plotter import Plotter
>
> plotter = Plotter(content="xcontent", module="xmodule",
                 edge_content="edge-xcontent", edge_module="edge-xmodule")
> plotter.produce_graphs("schematicresponse", 5, problem=True) 

The above example will create the graphs in a sensible directory with intuitive names. If problem is true then the script will look for problems containing the given tag, otherwise plotter will assume that you're looking for modules with the given category. A number of examples detailing currently known blades is at the bottom of the source file.

If you have any questions, or a feature request. Let Slater know.
