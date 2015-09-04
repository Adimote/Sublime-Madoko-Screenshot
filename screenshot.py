import sublime
import sublime_plugin
import subprocess
import re


class ScreenshotCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        image_path = self.get_snapshot()
        # Get the directory of the file
        file_path = self.view.file_name()
        file_dir = self.get_dir(file_path)

        # if the image directory is the same as the saved directory
        if file_dir == self.get_dir(image_path):
            # We can use the local path
            string = self.get_file_name(image_path)
        else:
            # Otherwise, use the full path.
            string = image_path

        self.replace_selected(
            self.view,
            edit,
            (
                "![{}]\n"
                "[{}]: {}"
                ""
            ).format(string, string, string)
        )

    def get_snapshot(self):
        """
            Takes the snapshot with a default location of the current file.
        """
        file_path = self.view.file_name()
        if file_path is None:
            raise sublime.error_message("Save File First")
        file_dir = self.get_dir(file_path)
        image_name = "test.png"
        image_path = file_dir + image_name
        return self.run_snapshot(image_path)

    def run_snapshot(self, image_path):
        """ Take a snapshot, block until the snapshot finishes """
        proc = subprocess.Popen([
            "shutter",
            "-s",
            "-e",
            "--disable_systray",
            "--debug",
            "-o",
            image_path,
        ],
            stdout=subprocess.PIPE)
        match = None
        while proc.returncode is None:
            try:
                line, err = proc.communicate(timeout=15)
            except subprocess.TimeoutExpired:
                print("TIMEOUT!")
                proc.terminate()
                line, err = proc.communicate()

            line = line.decode('ascii')

            # Check for line:
            # Saving file /media/1TB_SSD/notes/Selection_003.png,
            print("Out", line)
            m = re.search(".*(?:Saving file )([^,]*),.*", line,
                          flags=re.MULTILINE)
            if m is not None:
                # the real code does filtering here
                match = m.groups()[0]
                print("CAUGHT Save file: test:`", match, "`")
            # Find out whether the process has ended.
            proc.poll()
        print("Process finished!")
        # Shutter puts the result into the clipboard.
        return match

    def get_dir(self, file_path):
        # Get the directory of the file
        dir_end_match = re.search("[^/]*$", file_path)
        return file_path[:dir_end_match.start()]

    def get_file_name(self, file_path):
        # Get the directory of the file
        dir_end_match = re.search("[^/]*$", file_path)
        return file_path[dir_end_match.start():]

    def replace_selected(self, view, edit, text):
        # Replace all changed areas
        for region in view.sel():
            # Replace the selection with transformed text
            view.replace(edit, region, text)
