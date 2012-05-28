import sublime, sublime_plugin, time
from subprocess import check_call

SETTINGS_NAME = 'EclipseJavaFormatter'
SETTINGS = '%s.sublime-settings' % SETTINGS_NAME
KEY_ECLIPSE_COMMAND = 'eclipse_command'
KEY_NOSPLASH = 'no_splash'
KEY_VERBOSE = 'verbose'
KEY_CONFIG = 'config_file'

class EclipseFormatJavaCommand(sublime_plugin.TextCommand):

  def run_(self, args):
    view = self.view

    ''' save if there are unsaved changes '''
    if view.is_dirty():
      view.run_command('save')

    ''' cache line endings, as we may need to restore them '''
    #line_endings = view.line_endings()
    #self.__printLineEndings(line_endings)

    ''' do external call to eclipse formatter '''
    output = check_call(self.__assembleCommand())

    ''' reload formatted file '''
    view.run_command('revert')

    ''' restore line endings and save if they have changed '''
    #self.__printLineEndings(line_endings)
    #if (self.__determineLineEndings() != line_endings):
    #  view.set_line_endings(line_endings)
    #  view.run_command('save')
    #  self.__printLineEndings(line_endings)

  def __assembleCommand(self):
    args = []

    platform = sublime.platform()

    args.append(self.__getSetting(KEY_ECLIPSE_COMMAND))

    if self.__getSetting(KEY_NOSPLASH):
      args.append('-nosplash')

    args.append('-application')
    args.append('org.eclipse.jdt.core.JavaCodeFormatter')

    if self.__getSetting(KEY_VERBOSE):
      args.append('-verbose')

    args.append('-config')
    args.append(self.__getSetting(KEY_CONFIG))

    args.append(self.view.file_name())

    return args

  def __getSetting(self, key):
    view_settings = self.view.settings()
    if view_settings.has(SETTINGS_NAME):
      project_settings = view_settings.get(SETTINGS_NAME)
      for proj_setting_key in project_settings:
        if proj_setting_key == key:
          return project_settings[proj_setting_key]

    plugin_settings = sublime.load_settings(SETTINGS)
    return plugin_settings.get(key, None)

  def __determineLineEndings(self):
    lf_count = 0
    cr_count = 0
    crlf_count = 0

    f = open(self.view.file_name())
    for line in f.readlines():
      c = line[-1:]
      if c == '\n':
        if len(line) > 1 and line[-2:-1] == '\r':
          crlf_count+=1
        else:
          lf_count+=1
      elif c == '\r':
        cr_count+=1
    f.close()

    if lf_count > cr_count and lf_count > crlf_count:
      return 'Unix'
    elif crlf_count > lf_count and crlf_count > cr_count:
      return 'Windows'
    else:
      return 'Mac OS 9'

  def __printLineEndings(self, originalLineEndings=None):
    if originalLineEndings is not None:
      print 'original line endings: %s' % originalLineEndings
      print 'view line endings: %s' % self.view.line_endings()
      print 'file line endings: %s' % self.__determineLineEndings()
