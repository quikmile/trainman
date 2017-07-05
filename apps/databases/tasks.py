from celery.task import task
from django.conf import settings

from .models import PostgresNode, RedisNode
from ..base.ansibles import Runner
from ..custom.utils import remove_quotes


@task
def deploy_postgres(postgres_node_id):
    PLAYBOOK = settings.ANSIBLE_DIR + 'playbook.yml'
    hosts = ['[postgres]']

    postgres_node = PostgresNode.objects.get(pk=postgres_node_id)
    host = postgres_node.database_host

    hosts.append('{} ansible_user={} ansible_sudo_pass={}'.format(host,
                                                                  settings.ANSIBLE_SSH_USER,
                                                                  settings.ANSIBLE_SSH_PASS))

    postgres_extensions = list(postgres_node.postgres.database_extensions)

    sql = ''
    for ext in postgres_extensions:
        sql += 'create extension {};\n'.format(ext)
    sql += postgres_node.postgres.get_sql()

    tags = ['prepare', 'postgres']

    if 'postgis' in postgres_extensions:
        tags.append('postgis')

    run_data = {
        'sql': sql,
        'db_name': remove_quotes(postgres_node.database_name),
        'db_user': remove_quotes(postgres_node.database_user),
        'db_pass': remove_quotes(postgres_node.database_password)
    }

    hostnames = '\n'.join(hosts)

    runner = Runner(hostnames=hostnames,
                    playbook=PLAYBOOK,
                    private_key_file=settings.ANSIBLE_PUBLIC_KEY,
                    run_data=run_data,
                    become_pass=settings.ANSIBLE_SSH_PASS,
                    tags=tags)

    stats = runner.run()

    service = postgres_node.postgres.get_service()
    service.trellio_admin.deploy()


@task
def deploy_redis(redis_node_id, extra_tags=()):
    PLAYBOOK = settings.ANSIBLE_DIR + 'playbook.yml'
    hosts = ['[redis]']

    redis_node = RedisNode.objects.get(pk=redis_node_id)
    host = redis_node.database_host

    hosts.append('{} ansible_user={} ansible_sudo_pass={}'.format(host,
                                                                  settings.ANSIBLE_SSH_USER,
                                                                  settings.ANSIBLE_SSH_PASS))

    tags = ['redis']
    if extra_tags:
        tags.extend(extra_tags)

    run_data = {
    }

    hostnames = '\n'.join(hosts)

    runner = Runner(hostnames=hostnames,
                    playbook=PLAYBOOK,
                    private_key_file=settings.ANSIBLE_PUBLIC_KEY,
                    run_data=run_data,
                    become_pass=settings.ANSIBLE_SSH_PASS,
                    tags=tags)

    stats = runner.run()
