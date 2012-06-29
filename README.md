##Basic Config
At a minimum, include the following configuration block in either your user or project settings:

```JavaScript
"EclipseJavaFormatter":
{
  // you may not even need this one if eclipse is on your path
  "eclipse_command": "/path/to/eclipse/install/eclipse",

  "config_file": "/path/to/org.eclipse.jdt.core.prefs"
}
```

For information on how to find and/or generate your `config_file`, look here:
[Formatting your code using the Eclipse formatter](http://www.peterfriese.de/formatting-your-code-using-the-eclipse-code-formatter/)


##Line Endings
If you need to preserve your line endings, add the following:

```JavaScript
"restore_line_endings": true,
```

##Notes
If you use gradle and [SublimeJava](https://github.com/quarnster/SublimeJava)
for your java development, you may be interested in my 
[gradle plugin](https://github.com/phildopus/gradle-sublimetext-plugin).