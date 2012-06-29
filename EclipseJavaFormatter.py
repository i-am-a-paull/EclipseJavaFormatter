import sublime, sublime_plugin
from subprocess import Popen, PIPE

SETTINGS_NAME = 'EclipseJavaFormatter'
SETTINGS_FILE_NAME = '%s.sublime-settings' % SETTINGS_NAME
KEY_ECLIPSE_COMMAND = 'eclipse_command'
KEY_NOSPLASH = 'no_splash'
KEY_VERBOSE = 'verbose'
KEY_CONFIG = 'config_file'
KEY_RESTORE_ENDINGS = 'restore_line_endings'

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

    
