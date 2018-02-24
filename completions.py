import sublime, sublime_plugin, re, codecs, sys, os
from os import listdir
from os.path import isfile, join

class completions(sublime_plugin.EventListener):
    
    def on_query_completions(self, view, prefix, locations):
        cUserPackagePath    = sublime.packages_path()+'/User/sublime_hpsm/templates/'
        
        objConfig           = sublime.load_settings("hpsm.sublime-settings")

        autocomplete_config = objConfig.get('autocomplete')

        if not os.path.exists(cUserPackagePath):
            os.makedirs(cUserPackagePath)


        if len(autocomplete_config['prefix'])>0:
            if not prefix.startswith(autocomplete_config['prefix']):
                return []

        if len(prefix) <= autocomplete_config['min_length']:
            return []

        # Only trigger within js
        if not view.match_selector(locations[0], "source.hpsm"):
            return []

        #define path to the templates (core and user)
        cPackagePath        = sublime.packages_path()+'/sublime_hpsm/templates/'
        cUserPackagePath    = sublime.packages_path()+'/User/sublime_hpsm/templates/'

        #get all template files (core and user)
        arrFoundFiles       = listdir(cPackagePath)
        try :
            arrFoundUserFiles   = listdir(cUserPackagePath)
        except FileNotFoundError:
            arrFoundUserFiles = []


        arrReplacedFiles    = []
        
        #get core templates
        for cFilename in arrFoundFiles:
            if not cFilename.startswith('.') and isfile(cPackagePath+cFilename):
                #get filename without extension
                cCompletionName     = autocomplete_config['prefix']+os.path.splitext(cFilename)[0]
                #get content of the file with replaced placeholders
                cReplacedContent    = self.replacePlaceholder(cPackagePath+cFilename)
                #push the object to the array - will be returned later
                arrReplacedFiles.append(( cCompletionName , cReplacedContent ))

        #get user templates if available
        for cUserFilename in arrFoundUserFiles:
            if not cUserFilename.startswith('.') and isfile(cUserPackagePath+cUserFilename):
                #get filename without extension
                cUserCompletionName     = autocomplete_config['prefix']+os.path.splitext(cUserFilename)[0]
                #get content of the file with replaced placeholders
                cUserReplacedContent    = self.replacePlaceholder(cUserPackagePath+cUserFilename)
                #push the object to the array - will be returned later
                arrReplacedFiles.append(( cUserCompletionName , cUserReplacedContent ))


        return (arrReplacedFiles, 0)

    # function to replace placeholders in a file
    def replacePlaceholder(self, cFile):
        
        # initialize config
        objConfig           = sublime.load_settings("hpsm.sublime-settings")

        # open file as read only with utf-8 encoding
        cFile               = codecs.open(cFile, "r", "utf-8")

        # read file
        cReplaceText        = cFile.read()
        
        # set regex pattern
        cRegexPattern       = "{{Setting:(.*?)}}"

        # check text
        cRegexMatch         = re.search(cRegexPattern, cReplaceText)

        # replace all placeholders with the values from the settings
        for cRegexMatch in re.finditer(cRegexPattern, cReplaceText):
            cKey            = cRegexMatch.group(1)
            cReplaceText    = re.sub(cRegexPattern, objConfig.get(cKey), cReplaceText, 1)
        
        return cReplaceText