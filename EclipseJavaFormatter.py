import sublime, sublime_plugin, re, os
from operator import attrgetter
from subprocess import Popen, PIPE

SETTINGS_NAME = 'EclipseJavaFormatter'
SETTINGS_FILE_NAME = '%s.sublime-settings' % SETTINGS_NAME

KEY_ECLIPSE_COMMAND = 'eclipse_command'
KEY_NOSPLASH = 'no_splash'
KEY_VERBOSE = 'verbose'
KEY_CONFIG = 'config_file'
KEY_RESTORE_ENDINGS = 'restore_line_endings'

KEY_SORT_IMPORTS = 'sort_imports'
KEY_SORT_ORDER = 'sort_imports_order'

IMP_RE = 'import( static)? ([\w\.]+)\.([\w]+|\*);'
IMP_PROG = re.compile(IMP_RE)

LANG_RE = "^((source|text\.)[\w+\-\.#]+)"
LANG_PROG = re.compile(LANG_RE)

class EclipseFormatJavaCommand(sublime_plugin.TextCommand):

  def run_(self, args):
    ''' save if there are unsaved changes '''
    if self.view.is_dirty():
      self.view.run_command('save')

    ''' cache line endings, as we may need to restore them '''
    line_endings = self.view.line_endings()

    ''' do external call to eclipse formatter '''
    if self.__run_external_command(self.__assemble_eclipse_command()):
      edit = self.view.begin_edit()

      self.__refresh_view(edit)

      if self.__get_setting(KEY_SORT_IMPORTS):
        import_regions = self.view.find_all(IMP_RE)
        mega_region = import_regions[0].cover(import_regions[-1])

        imports = [JavaImport(self.view.substr(region)) for region in import_regions]
        sorter = ImportSorter(imports, self.__get_setting(KEY_SORT_ORDER))

        self.view.replace(edit, mega_region, str(sorter))

      ''' restore line endings '''
      if self.__get_setting(KEY_RESTORE_ENDINGS):
        self.view.set_line_endings(line_endings)

      self.view.end_edit(edit)

      self.view.run_command('save')

  def __run_external_command(self, args):
    child = Popen(args, stdout=PIPE, stderr=PIPE)
    output, error = child.communicate()
    print output

    if error:
      sublime.error_message(error)
      return False

    return True

  def __assemble_eclipse_command(self):
    args = []

    platform = sublime.platform()

    args.append(os.path.expanduser(self.__get_setting(KEY_ECLIPSE_COMMAND)))

    if self.__get_setting(KEY_NOSPLASH):
      args.append('-nosplash')

    args.append('-application')
    args.append('org.eclipse.jdt.core.JavaCodeFormatter')

    is_verbose = self.__get_setting(KEY_VERBOSE)
    if is_verbose:
      args.append('-verbose')

    args.append('-config')
    args.append(os.path.expanduser(self.__get_setting(KEY_CONFIG)))

    args.append(self.view.file_name())

    if is_verbose:
      print "running command: %s" % ' '.join(args)

    return args

  def __refresh_view(self, edit):
    document = sublime.Region(0, self.view.size())
    f = open(self.view.file_name())
    self.view.replace(edit, document, f.read())

  def __get_setting(self, key):
    view_settings = self.view.settings()
    if view_settings.has(SETTINGS_NAME):
      project_settings = view_settings.get(SETTINGS_NAME)
      for proj_setting_key in project_settings:
        if proj_setting_key == key:
          return project_settings[proj_setting_key]

    plugin_settings = sublime.load_settings(SETTINGS_FILE_NAME)
    return plugin_settings.get(key, None)

  def is_visible(self):
    return self.__get_language() == "source.java"

  def __get_language(self):
    view = self.view
    if view == None:
        view = sublime.active_window().active_view()
    cursor = view.sel()[0].a
    scope = view.scope_name(cursor).strip()
    language = LANG_PROG.search(scope)
    if language == None:
        return None
    return language.group(0)

class JavaImport(object):

  def __init__(self, imp_str):
    result = IMP_PROG.match(imp_str)

    self.is_static = True if result.group(1) else False
    self.package = result.group(2)
    self.java_type = result.group(3)
    self.imp_str = imp_str
    
  def __repr__(self):
    return self.imp_str

class ImportSorter(object):

  def __init__(self, imports, sort_order):
    self.imports = self.sort_imports(imports, sort_order)

  def sort_imports(self, imports, sort_order):
    '''
    sort alphabetically and then by package depth,
    reversed so that packages with similar substrings
    (java and javax) don't get confused

    '''
    specific_first = sorted(sort_order, reverse=True)
    pkg_depth = lambda package: len(package.split('.'))
    specific_first = sorted(specific_first, key=pkg_depth, reverse=True)

    '''
    create dict for grouping packages and populate

    '''
    groups_by_package = dict(zip((sort_order + ['other']), 
                                  [[] for package in sort_order] + [[]]))
    used = []
    for imp in imports:
      for package in specific_first:
        if imp.package.startswith(package):
          groups_by_package[package].append(imp)
          used.append(imp)
          break

    ''' other gets the dregs '''
    groups_by_package['other'] = [imp for imp in imports if imp not in used]

    sorted_groups = []
    for key in (sort_order + ['other']):
      if len(groups_by_package[key]) > 0:
        pkg_group = sorted(groups_by_package[key], key=attrgetter('java_type'))
        pkg_group = sorted(pkg_group, key=attrgetter('package'))
        sorted_groups.append(pkg_group)

    return sorted_groups

  def __repr_group(self, group):
    return '\n'.join([str(imp) for imp in group])

  def __repr__(self):
    return '\n\n'.join([self.__repr_group(group) for group in self.imports])
    
