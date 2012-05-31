import sublime, sublime_plugin
from subprocess import Popen, PIPE, STDOUT

SETTINGS_NAME = 'EclipseJavaFormatter'
SETTINGS_FILE_NAME = '%s.sublime-settings' % SETTINGS_NAME
KEY_ECLIPSE_COMMAND = 'eclipse_command'
KEY_NOSPLASH = 'no_splash'
KEY_VERBOSE = 'verbose'
KEY_CONFIG = 'config_file'
KEY_RESTORE_ENDINGS = 'restore_line_endings'
KEY_CONVERT_TO_DOS_COMMAND = 'convert_to_dos_command'
KEY_CONVERT_TO_UNIX_COMMAND = 'convert_to_unix_command'
KEY_CONVERT_TO_OS9_COMMAND = 'convert_to_os9_command'

PLATFORM_WIN = 'Windows'
PLATFORM_UNIX = 'Unix'
PLATFORM_OS9 = 'Mac OS 9'
CONVERT_COMMANDS = {PLATFORM_WIN: KEY_CONVERT_TO_DOS_COMMAND,
                    PLATFORM_UNIX: KEY_CONVERT_TO_UNIX_COMMAND,
                    PLATFORM_OS9: KEY_CONVERT_TO_OS9_COMMAND}

class EclipseFormatJavaCommand(sublime_plugin.TextCommand):

  def run_(self, args):
    view = self.view

    ''' save if there are unsaved changes '''
    if view.is_dirty():
      view.run_command('save')

    ''' cache line endings, as we may need to restore them '''
    line_endings = view.line_endings()

    ''' do external call to eclipse formatter '''
    self.__run_external_command(self.__assemble_eclipse_command())

    ''' restore line endings '''
    if self.__get_setting(KEY_RESTORE_ENDINGS):
      self.__run_external_command(self.__assemble_convert_command(line_endings))
    
    view.run_command('revert')

  def __run_external_command(self, args):
    child = Popen(args, stdout=PIPE, stderr=STDOUT)
    print child.communicate()[0]

  def __assemble_eclipse_command(self):
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

  def __assemble_convert_command(self, original_line_endings):
    args = self.__get_setting(CONVERT_COMMANDS[original_line_endings]).split(' ')
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

    
