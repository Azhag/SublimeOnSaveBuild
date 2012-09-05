import sublime
import sublime_plugin
import re
import functools

class SublimeOnSaveBuild(sublime_plugin.EventListener):
    def on_post_save(self, view):
        global_settings = sublime.load_settings(__name__ + '.sublime-settings')

        # See if we should build. A project level build_on_save setting
        # takes precedence. To be backward compatible, we assume the global
        # build_on_save to be true if not defined.
        should_build = view.settings().get('build_on_save', global_settings.get('build_on_save', True))

        # Load filename filter. Again, a project level setting takes precedence.
        filename_filter = view.settings().get('filename_filter', global_settings.get('filename_filter', '*'))

        # Check if we should automatically hide the build window 
        auto_hide_build_window = view.settings().get('auto_hide_build_window', global_settings.get('auto_hide_build_window', True))

        if not should_build:
            return

        if not re.search(filename_filter, view.file_name()):
            return

        # show the 'exec' view before building, so we can read from it afterwards
        self.output_view = view.window().get_output_panel("exec")

        view.window().run_command('build')

        if auto_hide_build_window:
            self.num_polls = 0
            # start polling for results every 100s
            self.poll_for_results(view)

    def poll_for_results(self, view):
        build_finished = self.output_view.find('Finished', 0) != None

        if build_finished:
            errors = self.output_view.find('Error', 0)
            if errors == None:
                view.window().run_command("hide_panel", {"panel": "output.exec"})
        else:            
            if self.num_polls < 300:
                sublime.set_timeout(functools.partial(self.poll_for_results, view), 200)

        self.num_polls += 1
