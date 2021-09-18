import os
import tempfile
import unittest
import subprocess

from unittest.mock import Mock, patch

from tfstack_executors import parse_process_output, grep_script_error, grep_resource_id, create_tf_stack, delete_tf_stack, read_tf_stack


class Test_executors_process(unittest.TestCase):
    def setUp(self):
        # This temporary file will act as a standard stream pipe for `Popen`
        self.stdout_mock = tempfile.NamedTemporaryFile(delete=False)

    def tearDown(self):
        # At the end of the test, we'll close and remove the created file
        self.stdout_mock.close()
        os.remove(self.stdout_mock.name)

    # Please, take care of "patching" to the right place
    @patch('subprocess.Popen')
    def test_parse_process_output(self, patch_popen):
        # We store some data into the fake pipe here
        self.stdout_mock.write(b'mocked stdout line 1\n')
        self.stdout_mock.write(b'mocked stdout line 2\n')

        # We have to rewind to the beginning of the file for the next reading
        self.stdout_mock.seek(0)

        expected_process_output = [
            'mocked stdout line 1', 'mocked stdout line 2']

        # The fake standard stream attribute is set here
        patch_popen.return_value.stdout = self.stdout_mock

        cmd = './create_tfstack.sh'
        process = subprocess.Popen(cmd,
                                   shell=True,
                                   executable='/bin/sh',
                                   stdout=subprocess.PIPE)

        # Run your test(s) !
        process_output_list = parse_process_output(process)
        self.assertEqual(process_output_list, expected_process_output)

    @patch('subprocess.Popen')
    def test_create_tf_stack(self, patch_popen):

        # We store some data into the fake pipe here
        self.stdout_mock.write(b'mocked stdout line 1\n')
        self.stdout_mock.write(b'resource_id "123"\n')

        # We have to rewind to the beginning of the file for the next reading
        self.stdout_mock.seek(0)

        # The fake standard stream attribute is set here
        patch_popen.return_value.stdout = self.stdout_mock
        patch_popen.return_value.returncode = 0

        self.assertEqual(create_tf_stack('some_dir'), {
                         'message': 'TFstack created succesfully', 'resource_id': '123'})

    @patch('subprocess.Popen')
    def test_create_tf_stack_scripterror(self, patch_popen):

        # We store some data into the fake pipe here
        self.stdout_mock.write(b'mocked stdout line 1\n')
        self.stdout_mock.write(b'error:ExistingWorkspaceContainsResources\n')

        # We have to rewind to the beginning of the file for the next reading
        self.stdout_mock.seek(0)

        # The fake standard stream attribute is set here
        patch_popen.return_value.stdout = self.stdout_mock
        patch_popen.return_value.returncode = 1

        with self.assertRaises(Exception) as cm:
            create_tf_stack('some_dir')
        self.assertEqual(
            'error:ExistingWorkspaceContainsResources',
            str(cm.exception)
        )

    @patch('subprocess.Popen')
    def test_delete_tf_stack(self, patch_popen):

        # We store some data into the fake pipe here
        self.stdout_mock.write(b'mocked stdout line 1\n')

        # We have to rewind to the beginning of the file for the next reading
        self.stdout_mock.seek(0)

        # The fake standard stream attribute is set here
        patch_popen.return_value.stdout = self.stdout_mock
        patch_popen.return_value.returncode = 0

        self.assertEqual(delete_tf_stack('some_dir', '123'), {
            'message': "TFstack deleted succesfully"})

    @patch('subprocess.Popen')
    def test_delete_tf_stack_scripterror(self, patch_popen):
        # We store some data into the fake pipe here
        self.stdout_mock.write(b'mocked stdout line 1\n')
        self.stdout_mock.write(b'error:WorkspaceNotExist\n')

        # We have to rewind to the beginning of the file for the next reading
        self.stdout_mock.seek(0)

        # The fake standard stream attribute is set here
        patch_popen.return_value.stdout = self.stdout_mock
        patch_popen.return_value.returncode = 1

        with self.assertRaises(Exception) as cm:
            delete_tf_stack('some_dir', '123')
        self.assertEqual(
            'error:WorkspaceNotExist',
            str(cm.exception)
        )

    @patch('subprocess.Popen')
    def test_read_tf_stack(self, patch_popen):
        # We store some data into the fake pipe here
        self.stdout_mock.write(b'mocked stdout line 1\n')

        # We have to rewind to the beginning of the file for the next reading
        self.stdout_mock.seek(0)

        # The fake standard stream attribute is set here
        patch_popen.return_value.stdout = self.stdout_mock
        patch_popen.return_value.returncode = 0

        self.assertEqual(read_tf_stack('some_dir', '123'), {
            'message': "TFstack read succesfully",
            'content': ['mocked stdout line 1'],
        })

    @patch('subprocess.Popen')
    def test_read_tf_stack_error(self, patch_popen):
        # We store some data into the fake pipe here
        self.stdout_mock.write(b'mocked stdout line 1\n')
        self.stdout_mock.write(b'error:WorkspaceNotExist\n')

        # We have to rewind to the beginning of the file for the next reading
        self.stdout_mock.seek(0)

        # The fake standard stream attribute is set here
        patch_popen.return_value.stdout = self.stdout_mock
        patch_popen.return_value.returncode = 1

        with self.assertRaises(Exception) as cm:
            read_tf_stack('some_dir', '123')
        self.assertEqual(
            'error:WorkspaceNotExist',
            str(cm.exception)
        )


class Test_executors_other(unittest.TestCase):
    def test_grep_script_error_match(self):
        found_error = grep_script_error(
            ['foobar', 'error1', 'error2'], ['error1'])
        self.assertEqual(found_error, 'error1')

    def test_grep_script_error_unmatched(self):
        found_error = grep_script_error(
            ['foobar', 'foobar2'], ['error1'])
        self.assertEqual(found_error, None)

    def test_grep_resource_id_match(self):
        process_output = ['foobar', 'resource_id "123"']
        found_resource_id = grep_resource_id(
            process_output=process_output, resource_id_grep_pattern='resource_id')
        self.assertEqual(found_resource_id, '123')

    def test_grep_resource_id_unmatched(self):
        process_output = ['foobar', 'error1', 'error2']
        found_resource_id = grep_resource_id(
            process_output=process_output, resource_id_grep_pattern='resource_id')
        self.assertEqual(found_resource_id, None)


if __name__ == '__main__':
    unittest.main()
