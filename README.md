##Basic Config
At a minimum, include the following configuration block in either your user or project settings:

```JavaScript
"EclipseJavaFormatter":
{
  // you may not need this one if eclipse is on your path
  "eclipse_command": "/path/to/eclipse/install/eclipse",

  "config_file": "/path/to/org.eclipse.jdt.core.prefs"
}
```

For information on how to find and/or generate your `config_file`, look here:
[Formatting your code using the Eclipse formatter](http://www.peterfriese.de/formatting-your-code-using-the-eclipse-code-formatter/)


##Line Endings
Some other important settings deal with line endings.  Since this is something that may not even be an issue for some, I relegated this to an external command, as well.  Just in case you would have different utilities to deal with individual line ending types (such as dos2unix and unix2dos), I've made each newline utility its own config key (`convert_to_<platform>_command`).  I've become partial to [flip](https://ccrma.stanford.edu/~craig/utility/flip/).

```JavaScript
"restore_line_endings": true,

// the next three must be set if restore_line_endings is true
"convert_to_dos_command": "/Users/phildopus/Applications/bin/flip -d",

"convert_to_unix_command": "/Users/phildopus/Applications/bin/flip -u",

"convert_to_os9_command": "/Users/phildopus/Applications/bin/flip -m"
```

##Notes
If you use gradle and [SublimeJava](https://github.com/quarnster/SublimeJava)
for your java development, you may be interested in my 
[gradle plugin](https://github.com/phildopus/gradle-sublimetext-plugin).