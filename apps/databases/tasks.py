from celery.task import task
from django.conf import settings

from .models import PostgresNode, RedisNode
from ..base.ansibles import Runner


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
    tags = ['prepare', 'postgres']

    if 'postgis' in postgres_extensions:
        tags.append('postgis')

    run_data = {
        'postgres_extensions': postgres_extensions,
        'db_name': postgres_node.database_name,
        'db_user': postgres_node.database_user,
        'db_pass': postgres_node.database_password
    }

    hostnames = '\n'.join(hosts)

    runner = Runner(hostnames=hostnames,
                    playbook=PLAYBOOK,
                    private_key_file=settings.ANSIBLE_PRIVATE_KEY,
                    run_data=run_data,
                    become_pass=settings.ANSIBLE_SSH_PASS,
                    tags=tags)

    stats = runner.run()


@task
def deploy_redis(redis_node_id):
    PLAYBOOK = settings.ANSIBLE_DIR + 'playbook.yml'
    hosts = ['[redis]']

    redis_node = RedisNode.objects.get(pk=redis_node_id)
    host = redis_node.database_host

    hosts.append('{} ansible_user={} ansible_sudo_pass={}'.format(host,
                                                                  settings.ANSIBLE_SSH_USER,
                                                                  settings.ANSIBLE_SSH_PASS))

    tags = ['prepare', 'redis']

    run_data = {
    }

    hostnames = '\n'.join(hosts)

    runner = Runner(hostnames=hostnames,
                    playbook=PLAYBOOK,
                    private_key_file=settings.ANSIBLE_PRIVATE_KEY,
                    run_data=run_data,
                    become_pass=settings.ANSIBLE_SSH_PASS,
                    tags=tags)

    stats = runner.run()
