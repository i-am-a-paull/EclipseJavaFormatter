import sublime, sublime_plugin
from subprocess import Popen, PIPE, STDOUT

SETTINGS_NAME = 'EclipseJavaFormatter'
SETTINGS_FILE_NAME = '%s.sublime-settings' % SETTINGS_NAME
KEY_ECLIPSE_COMMAND = 'eclipse_command'
KEY_NOSPLASH = 'no_splash'
KEY_VERBOSE = 'verbose'
KEY_CONFIG = 'config_file'
KEY_RESTORE_ENDINGS = 'restore_line_endings'

PLATFORM_WIN = 'Windows'
PLATFORM_UNIX = 'Unix'
PLATFORM_OS9 = 'Mac OS 9'
ENDING_CRLF = '/r/n'
ENDING_LF = '/n'
ENDING_CR = '/r'
ENDINGS = {PLATFORM_WIN: ENDING_CRLF,
           PLATFORM_UNIX: ENDING_LF,
           PLATFORM_OS9: ENDING_CR}

class EclipseFormatJavaCommand(sublime_plugin.TextCommand):

  def run(self, edit):
    view = self.view

    ''' save if there are unsaved changes '''
    if view.is_dirty():
      view.run_command('save')

    ''' cache line endings, as we may need to restore them '''
    line_endings = view.line_endings()

    ''' do external call to eclipse formatter '''
    child = Popen(self.__assemble_command(), stdout=PIPE, stderr=STDOUT)
    print child.communicate()[0]

    if self.__get_setting(KEY_RESTORE_ENDINGS):
      ''' restore line endings and save '''
      #self.__restore_line_endings(line_endings)
      #view.run_command('save')
      pass
    else:
      ''' reload formatted file as-is '''
      view.run_command('revert')

  def __assemble_command(self):
    args = []

    platform = sublime.platform()

    args.append(self.__get_setting(KEY_ECLIPSE_COMMAND))

    if self.__get_setting(KEY_NOSPLASH):
      args.append('-nosplash')

    args.append('-application')
    args.append('org.eclipse.jdt.core.JavaCodeFormatter')

    if self.__get_setting(KEY_VERBOSE):
      args.append('-verbose')

    args.append('-config')
    args.append(self.__get_setting(KEY_CONFIG))

    args.append(self.view.file_name())

    return args

  def __get_setting(self, key):
    view_settings = self.view.settings()
    if view_settings.has(SETTINGS_NAME):
      project_settings = view_settings.get(SETTINGS_NAME)
      for proj_setting_key in project_settings:
        if proj_setting_key == key:
          return project_settings[proj_setting_key]

    plugin_settings = sublime.load_settings(SETTINGS_FILE_NAME)
    return plugin_settings.get(key, None)

  def __restore_line_endings(self, original_line_endings):
    v = self.view
    ed = v.begin_edit()
    v.erase(ed, sublime.Region(0, v.size()))

    '''cursor = 0
    f = open(v.file_name())
    for line in f.readlines():
      cursor+=v.insert(ed, cursor, line.rstrip())
      #cursor+=v.insert(ed, cursor, ENDINGS[original_line_endings])
    f.close()'''

    v.end_edit(ed)
