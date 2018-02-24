import sublime, sublime_plugin, re, codecs, sys, os
from os import listdir
from os.path import isfile, join
import json, difflib, tempfile
from fnmatch import fnmatch
from base64 import b64encode
#load third party modules
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))
import httplib2


#Global function to get settings
#this is a workaround, because if we load "settings" as global variable
#the object is sometimes empty and sublime will throw an error
def get_setting(name, default=None):

    settings = sublime.load_settings('hpsm.sublime-settings')
    v = settings.get(name)

    if v == None:
        try:
            return sublime.active_window().active_view().settings().get(name, default)
        except AttributeError:
            # No view defined.
            return default
    else:
        return v

httplib2.debuglevel = get_setting('debug',0)

#GET Request Helper Function
def getRequest(libraryname=None, environment=None):
    
    if (environment == None):
        return None

    environments    = get_setting("environments")
    selected_env    = environments[environment]

    h           = httplib2.Http("")
    headers     = {}
    try:

        #build request url
        if (libraryname == None):
            serverurl   = selected_env['servername']+selected_env['serverport']+selected_env['api_path']+selected_env['api_service']
        else:
            serverurl   = selected_env['servername']+selected_env['serverport']+selected_env['api_path']+selected_env['api_service']+"/"+libraryname

        #set basic auth
        if (selected_env['username'] and selected_env['password'] ): 
            username    = selected_env['username']
            password    = selected_env['password']
            auth        = b64encode( bytes(username + ':' + password, 'utf-8') ).decode("ascii")
            headers     = { 'Authorization' : 'Basic %s' %  auth }

        #get the response
        response, content=h.request(serverurl, "GET", headers=headers)

        #if request was successul
        if response.status == 200:
            #convert the bytes object first to a string and then to a json object
            contents        = json.loads(content.decode("utf-8"))
            return contents
            
        #unauthorized
        if response.status == 401:
            sublime.status_message("HPSM Error: Not authorized")
            return None
    except: # catch *all* exceptions
        e = sys.exc_info()[1]

        print(e)

        sublime.status_message("Error: %s" % e)
        return None    

#POST Request Helper Function
def postRequest(filepath, filename, environment=None):

    if (environment == None):
        return None

    environments    = get_setting("environments")
    selected_env    = environments[environment]

    h           = httplib2.Http("")
    headers     = {'Content-Type': 'application/json'}
    library     = getRequest(filename, environment)

    try:

        #build request url
        if (library == None):
            #create new library
            serverurl   = selected_env['servername']+selected_env['serverport']+selected_env['api_path']+selected_env['api_service']
            with codecs.open(filepath, "r", 'utf-8') as myfile:
                data                                = {}
                data[selected_env['api_service']]   = { 'Name' : filename, 'Package': selected_env['default_package'], 'Script': myfile.read()}
        else:
            #update existing library
            serverurl   = selected_env['servername']+selected_env['serverport']+selected_env['api_path']+selected_env['api_service']+"/"+filename
            with codecs.open(filepath, "r", 'utf-8') as myfile:
                data                                = {}
                data[selected_env['api_service']]   = { 'Script' : myfile.read()}

        #set basic auth
        if ( selected_env['username'] and selected_env['password'] ): 
            username    = selected_env['username']
            password    = selected_env['password']
            auth        = b64encode( bytes(username + ':' + password, 'utf-8') ).decode("ascii")
            headers     = { 'Authorization' : 'Basic %s' %  auth }
            
        #get the response
        response, content=h.request(serverurl, "POST", body=json.dumps(data), headers=headers)

        #convert the bytes object first to a string and then to a json object
        content         = json.loads(content.decode("utf-8"))
        
        #if request was successul
        if response.status == 200:
            sublime.status_message(content['Messages'][0])
            return content
        if response.status == 400:
            sublime.status_message("Validation: "+content['Messages'][0])
            return content

        #unauthorized
        if response.status == 401:
            sublime.status_message("HPSM Error: Not authorized")
            return content


    except httplib2.ServerNotFoundError:
        #show popup with error message
        sublime.status_message("HPSM is not available");
        return None     

#PUT Request Helper Function
def compileRequest(filename, environment=None):

    if (environment == None):
        return None

    environments    = get_setting("environments")
    selected_env    = environments[environment]

    h           = httplib2.Http("")
    headers     = {'Content-Type': 'application/json'}
    library     = getRequest(filename, environment)
    try:

        #build request url
        if (library == None):
            return None
        else:
            serverurl   = selected_env['servername']+selected_env['serverport']+selected_env['api_path']+selected_env['api_service']+"/"+filename+"/action/compile"
            data                                = {}
            data[selected_env['api_service']]   = { 'Name' : filename }

        #set basic auth
        if (selected_env['username'] and selected_env['password'] ): 
            username    = selected_env['username']
            password    = selected_env['password']
            auth        = b64encode( bytes(username + ':' + password, 'utf-8') ).decode("ascii")
            headers     = { 'Authorization' : 'Basic %s' %  auth }
            
        #get the response
        response, content=h.request(serverurl, "POST", body=json.dumps(data), headers=headers)

        #convert the bytes object first to a string and then to a json object
        content         = json.loads(content.decode("utf-8"))
        
        #print("response: ",response)

        #if request was successul
        if response.status == 200:
            sublime.status_message(content['Messages'][0])
            return content

        if response.status == 400:
            sublime.status_message("Validation: "+content['Messages'][0])
            return content

        #unauthorized
        if response.status == 401:
            sublime.status_message("HPSM Error: Not authorized")
            return content


    except httplib2.ServerNotFoundError:
        #show popup with error message
        sublime.status_message("HPSM is not available");
        return None             

#Create File
class HpsmSlCreateCommand(sublime_plugin.TextCommand):

    #create / update file 
    def create(self, libraryname, open_new=True, environment=None):

        if (environment == None):
            return None

        environments    = get_setting("environments")
        selected_env    = environments[environment]

        #get ScriptLibrary Record
        contents = getRequest(libraryname, environment)

        if(contents is None):
            sublime.status_message("Library with the Name '"+libraryname+"' not found in HPSM")
            return

        #open/create file and write content into the file
        #it will overwrite the existing content
        filename = selected_env['destination']+contents[selected_env['api_service']]['Name']+selected_env['file_ext']
        fFile = codecs.open(filename, 'w','utf-8') 
        fFile.write(contents[selected_env['api_service']].get('Script', ""))
        fFile.close()
        
        if(open_new):
            #open the file in a new tab with JS (HPSM) syntax highlighting
            scratch = self.view.window().open_file(filename)
            scratch.set_scratch(True)
            scratch.set_syntax_file('Packages/sublime_hpsm/JavaScript-HPSM.sublime-syntax')


class ShowCompileLogCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):

        if(len(args['Messages'])>1):
            n = sublime.active_window().new_file()
            n.set_scratch(True)
            n.set_name("Compile Error log")
            n.insert(edit, 0, "\n".join(args['Messages']))
        else:
            sublime.status_message(args['Messages'][0]) 

#post file to HPSM
class HpsmSlPushCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        active_filename = os.path.basename(os.path.splitext(self.view.file_name())[0])
        active_filepath = self.view.file_name()

        entries     = []
        
        environments        = get_setting("environments")
        environments_list   = list(environments)
      
        #push the found posts title to the array for the selection in the quick panel menu
        for key,environment in environments.items():
            entries.append(environments[key]['displayname'])
       
        #This will be called, if you select one of the entry
        def on_done(index):
            if index == -1:
                return

            if index > -1:
                response    = postRequest(active_filepath, active_filename, environments_list[index]) 
        
        # submenu
        sublime.set_timeout(lambda: self.view.window().show_quick_panel(entries, on_done), 1)

#get file from HPSM
class HpsmSlPullCommand(HpsmSlCreateCommand):  
    def run(self, edit):

        active_filename = os.path.basename(os.path.splitext(self.view.file_name())[0])
        active_filepath = self.view.file_name()

        entries     = []
        
        environments        = get_setting("environments")
        environments_list   = list(environments)
      
        #push the found posts title to the array for the selection in the quick panel menu
        for key,environment in environments.items():
            entries.append(environments[key]['displayname'])
       
        #This will be called, if you select one of the entry
        def on_done(index):
            if index == -1:
                return

            if index > -1:
                self.create(active_filename, False, environments_list[index]) 
        
        # submenu
        sublime.set_timeout(lambda: self.view.window().show_quick_panel(entries, on_done), 1)

#compile file to HPSM
class HpsmSlCompileCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        active_filename = os.path.basename(os.path.splitext(self.view.file_name())[0])
    
        entries     = []
        
        environments        = get_setting("environments")
        environments_list   = list(environments)
      
        #push the found posts title to the array for the selection in the quick panel menu
        for key,environment in environments.items():
            entries.append(environments[key]['displayname'])
       
        #This will be called, if you select one of the entry
        def on_done(index):
            if index == -1:
                return

            if index > -1:
                response = self.compile_log(active_filename, environments_list[index]) 
        
        # submenu
        sublime.set_timeout(lambda: self.view.window().show_quick_panel(entries, on_done), 1)

        #show compile log in case, that an error occours
    def compile_log(self, libraryname, environment=None):

        #get ScriptLibrary Record
        contents = compileRequest(libraryname, environment)

        if(contents is None):
            sublime.status_message("Library with the Name '"+libraryname+"' not found in HPSM in Environment: "+environment)
            return

        sublime.set_timeout_async(lambda: self.view.run_command("show_compile_log", contents), 0)
     
#Get Available ScriptLibraries
class GetLibrariesCommand(HpsmSlCreateCommand):

    def run(self, edit, **args):
        
        entries         = []
        contents        = getRequest(None,args["environment"])
        
        environments    = get_setting("environments")
        selected_env    = environments[args["environment"]]

        if(contents != None):
            #show number of found records in the status bar
            sublime.status_message("Libraries found: "+str(len(contents['content'])))
                
            #push the found posts title to the array for the selection in the quick panel menu
            for record in contents['content']:
                entries.append(record[selected_env['api_service']]['Name'])

        #This will be called, if you select one of the entry
        def on_done(index):
            if index == -1:
                return

            if index > -1:
                self.create(contents['content'][index][selected_env['api_service']]['Name'], True, args["environment"])
        
        #show second submenu
        sublime.set_timeout(lambda: self.view.window().show_quick_panel(entries, on_done), 1)

#Get Environments
class ShowEnvironmentsCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        
        entries     = []
        
        environments        = get_setting("environments")
        environments_list   = list(environments)
      
        #push the found posts title to the array for the selection in the quick panel menu
        for key,environment in environments.items():
            entries.append(environments[key]['displayname'])
       
        #This will be called, if you select one of the entry
        def on_done(index):
            if index == -1:
                return

            if index > -1:
                self.view.run_command('get_libraries', {"environment" : environments_list[index]} )
        
        # submenu
        sublime.set_timeout(lambda: self.view.window().show_quick_panel(entries, on_done), 1)
