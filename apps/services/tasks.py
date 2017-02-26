from celery.task.base import task
from django.conf import settings

from .models import ServiceRegistryNode
from ..base.ansibles import Runner


@task
def deploy_registry(registry_node_id):
    PLAYBOOK = settings.ANSIBLE_DIR + 'playbook.yml'
    hosts = ['[service_registry]']

    registry_node = ServiceRegistryNode.objects.get(pk=registry_node_id)
    host = registry_node.registry_host

    hosts.append('{} ansible_user={} ansible_sudo_pass={}'.format(host,
                                                                  settings.ANSIBLE_SSH_USER,
                                                                  settings.ANSIBLE_SSH_PASS))

    tags = ['prepare', 'trellio', 'registry']

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
