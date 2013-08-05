import cmislib
from django.http import HttpResponse

cmisClient = cmislib.CmisClient('https://gsb-contentqa.stanford.edu/alfresco/s/cmis', 'stanford', '2zj6C2u6WCms')

repo = cmisClient.defaultRepository #gets first repo in list
root = repo.getRootFolder()

def create_new_folder(name, parent_folder):
	folder = repo.createFolder(parent_folder, name)
	print folder.getTitle()
	return folder

def create_new_document(parent_folder, name, contFile):
	doc = parent_folder.createDocument(name, contentFile=contFile)
	print doc.getTitle()
	return doc

def print_root_contents():
	str = "<html><body>"
	for child in root.getChildren():
		print child.getTitle()
		str += child.getTitle()
	str+="</body></html>"
	return HttpResponse(str)
	
