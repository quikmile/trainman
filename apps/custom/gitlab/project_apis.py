from .base import Gitlab


class GitlabProject(Gitlab):
    @classmethod
    def get_project_tree(cls, project_id):
        return cls.get('projects/{}/repository/tree/'.format(project_id))

    @classmethod
    def get_dir_name(cls, project_id):
        result = cls.get_project_tree(project_id)
        return [i['path'] for i in result if i['type'] == 'tree'][0]

    @classmethod
    def read_file(cls, project_id, file_path):
        url = 'projects/{project_id}/repository/files/?file_path={file_path}&ref=master'
        result = cls.get(url.format(project_id=project_id, file_path=file_path))
        return cls.decode_content(result['content'])

    @classmethod
    def get_sql(cls, project_id):
        tree = cls.get_project_tree(project_id)
        sql_files = [i['path'] for i in tree if '.sql' in i['path']]
        sql = ''
        for file in sql_files:
            sql += cls.read_file(project_id, file)
        return sql
