from celery.task.base import task
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Postgres, PostgresNode


@receiver(post_save, sender=Postgres)
def initiate_postgres_tasks(sender, instance, **kwargs):
    create_postgres_nodes.delay(instance.id)


@receiver(post_save, sender=PostgresNode)
def initiate_postgres_nodes_tasks(sender, instance, **kwargs):
    deploy_postgres.delay(instance.id)


@task
def create_postgres_nodes(postgres_id):
    postgres = Postgres.objects.get(id=id)

    postgres_node = PostgresNode()
    postgres_node.postgres = postgres
    postgres_node.database_host = postgres.server.ip_address
    postgres_node.save()


@task
def deploy_postgres(postgres_node_id):
    PLAYBOOK = settings.ANSIBLE_DIR + 'playbook.yml'
    hosts = ['[postgres]']

    postgres_node = PostgresNode.objects.get(pk=postgres_node_id)
    host = postgres_node.database_host

    hosts.append('{} ansible_user={} ansible_sudo_pass={}'.format(host,
                                                                  settings.ANSIBLE_SSH_USER,
                                                                  settings.ANSIBLE_SSH_PASS))

    run_data = {
        'services': services
    }

    hostnames = '\n'.join(hosts)

    runner = Runner(hostnames=hostnames,
                    playbook=PLAYBOOK,
                    private_key_file=settings.ANSIBLE_PRIVATE_KEY,
                    run_data=run_data,
                    become_pass=settings.ANSIBLE_SSH_PASS,
                    tags=['prepare', 'nginx', 'gateway'])

    stats = runner.run()
