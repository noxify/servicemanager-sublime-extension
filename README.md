# Service Manager Sublime Extension

A Sublime Text package which allows you to create and modify Service Manager ScriptLibraries outside the Service Manager Client.

# Features

* Multiple Environments
* Create a new ScriptLibrary from a local file
* Push and Pull for ScriptLibraries
* Compile
* Code Snippets with auto-complete
* (Soon) Syntax Highlighting

# Installation

* Download the Repository
* Extract the zip archive and rename it from `sublime_hpsm-master` to `sublime_hpsm` 
* Browse to your Sublime Text Packages directory (There is a menu entry in Sublime if you don't know where the packages are stored)
* Copy the `sublime_hpsm` into the `Packages` directory

Note: If you have also `Package Control` installed, please add `"remove_orphaned": true,` to your `Package Control User Settings`. Otherwise the package will be removed.

Inside the Service Manager, you have to create a new `extaccess` record.

Please ensure that the used operator has enough permissions to create/update/compile a ScriptLibrary and that the capability `RESTful API` is set in the operator.

### Header fields

| Field Name   | Value         |
| ------------ | ------------- |
| Service Name | ScriptLibrary |
| Name         | ScriptLibrary |
| Object Name  | ScriptLibrary |

### Tab Allowed Actions

| Allowed Actions | Action Names | Action Type |
| --------------- | ------------ | ----------- |
| add             | Create       | Create only |
| save            | Update       | Update only |
| compile         | Compile      | <empty>     |

### Tab Fields

| Field   | Caption | Type    |
| ------- | ------- | ------- |
| name    | Name    | <empty> |
| package | Package | <empty> |
| script  | Script  | <empty> |

```
In this package, you can't use different captions - sorry.
```

### Tab RESTful

| Field                             | Value         |
| --------------------------------- | ------------- |
| RESTful enabled                   | true          |
| Resource Collection Name          | ScriptLibrary |
| Resource Name                     | ScriptLibrary |
| Unique Keys                       | name          |
| Resource Collection Action - POST | Create        |
| Resource Actions - POST           | Update        |
| Resource Actions - PUT            | Compile       |

If you're using a different Resource Collection Name and/or Resource Name, you have to modify also the extension settings. See `api_serivce` inside the configuration. This package requires the same name for the `Resource Collection Name` and `Resource Name`.


# Configuration

```
{
	"Fullname"		: "Marcus Reinhardt",
	"Shortname"		: "MR",
	"Company"		: "",
	"Email"			: "webstone@gmail.com",
	"CurrentYear"	: "2018",

	"environments"	: {

		"development"	: {
			"displayname"		: "Development Environment",
			"servername" 		: "http://127.0.0.1",
			"serverport" 		: ":13080",
			"username"	 		: "DEVAdminUsername",
			"password"	 		: "DEVAdminPassword",
			"api_path"	 		: "/SM/9/rest/",
			"api_service"		: "ScriptLibrary",
			
			"destination"		: "/Library/Path/Development/",
			"file_ext"			: ".js",

			"default_package" 	: "User"
		}
	},
	
	"autocomplete"	: {
		"prefix"		: "",
		"min_length"	: 2
	},

	"debug"				: 0
	
}
```

# Code Snippets

I'm a lazy guy and I hate to repeat myself over and over again - This is the reason why I built this extension.

It allows to define unlimited code snippets as JS file.
it allows you also to define a tab completion.
With this, you can speed up yourself - Yeah!

If you want to use your own code snippets, you have to go to `Preferences > Package Settings > HPSM > Browse User Templates`.

This packages comes with the following auto-complete templates:

## hpsm-nullsub

```
system.functions.nullsub( ${0:argument}, ${1:fallback} );
```

## hpsm-scfile-basic

```
var f${0:File} 	= new SCFile( "${1:tablename}" );
var q${0:File} 	= true;
var rc${0:File} = f${0:File}.doSelect( q${0:File} );
```

## hpsm-scfile-complete

```
var f${0:File} = new SCFile( "${1:tablename}" );
var q${0:File} = true; 
var rc${0:File} = f${0:File}.doSelect( q${0:File} );

while( rc${0:File} == RC_SUCCESS ) {
	//your code 
	rc${0:File} = f${0:File}.getNext();
}
```

You can also fetch values from the settings.

```
{{Setting:Fullname}}
```

`Fullname` is the key from the settings file - You can add also new keys to the `user` config.

# Credits

Special thanks goes to:

* [yim OHG](https://www.y-im.de) - My old company :heart: My first version was built there and now I will continue with the package as Open Source Project
