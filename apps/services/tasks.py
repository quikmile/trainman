from celery.task.base import task
from django.conf import settings

from .models import ServiceRegistryNode, ServiceNode
from ..base.ansibles import Runner
from ..servers.tasks import deploy_gateway


@task
def deploy_registry(registry_node_id, extra_tags=()):
    PLAYBOOK = settings.ANSIBLE_DIR + 'playbook.yml'
    hosts = ['[service_registry]']

    registry_node = ServiceRegistryNode.objects.get(pk=registry_node_id)
    host = registry_node.registry_host

    hosts.append('{} ansible_user={} ansible_sudo_pass={}'.format(host,
                                                                  settings.ANSIBLE_SSH_USER,
                                                                  settings.ANSIBLE_SSH_PASS))

    tags = ['trellio', 'registry']
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


@task
def deploy_service(service_node_id):
    service_node = ServiceNode.objects.get(pk=service_node_id)

    database = service_node.get_database()
    database.deploy()

    PLAYBOOK = settings.ANSIBLE_PLAYBOOK
    hosts = ['[trellio_service]']

    host = service_node.instance.server.ip_address

    hosts.append('{} ansible_user={} ansible_sudo_pass={}'.format(host,
                                                                  settings.ANSIBLE_SSH_USER,
                                                                  settings.ANSIBLE_SSH_PASS))

    tags = ['prepare', 'trellio', 'service']

    config = service_node.get_config()
    run_data = {
        'pip_repo_url': service_node.pip_repo_url,
        'git_repo_url': service_node.git_repo_url,
        'project_name': service_node.service_verbose_name,
        'service_name': service_node.get_service_directory(),
        'gitlab_username': settings.GITLAB_USERNAME,
        'gitlab_password': settings.GITLAB_PASSWORD
    }

    run_data.update(config)

    hostnames = '\n'.join(hosts)

    runner = Runner(hostnames=hostnames,
                    playbook=PLAYBOOK,
                    private_key_file=settings.ANSIBLE_PUBLIC_KEY,
                    run_data=run_data,
                    become_pass=settings.ANSIBLE_SSH_PASS,
                    tags=tags)

    stats = runner.run()

    deploy_gateway.delay()
