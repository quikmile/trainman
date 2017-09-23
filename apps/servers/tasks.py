from celery.task.base import task
from django.conf import settings

from .models import APIGateway
from .models import Server
from ..base.ansibles import Runner
from ..services.models import ServiceNode


@task
def deploy_gateway(gateway_id, email='', extra_tags=()):
    hosts = ['[gateway]']
    gateway = APIGateway.objects.get(pk=gateway_id)

    hosts.append('{} ansible_user={} ansible_sudo_pass={}'.format(gateway.server.ip_address,
                                                                  settings.ANSIBLE_SSH_USER,
                                                                  settings.ANSIBLE_SSH_PASS))

    if not email:
        try:
            email = settings.ADMINS[0][1]
        except:
            email = ''

    run_data = {'services': ServiceNode.objects.all(),
                'hostname': gateway.domain,
                'email': email}

    hostnames = '\n'.join(hosts)

    tags = list(extra_tags) + ['gateway']

    runner = Runner(hostnames=hostnames,
                    playbook=settings.ANSIBLE_PLAYBOOK,
                    private_key_file=settings.ANSIBLE_PUBLIC_KEY,
                    run_data=run_data,
                    become_pass=settings.ANSIBLE_SSH_PASS,
                    tags=tags)

    stats = runner.run()


@task
def server_setup(service_id, extra_tags=()):
    server = Server.objects.get(pk=service_id)

    hosts = ['[server]']
    hosts.append('{} ansible_user={}'.format(server.ip_address, 'root'))

    hostnames = '\n'.join(hosts)
    tags = list(extra_tags) + ['setup', 'prepare']

    run_data = {
        'user': settings.ANSIBLE_SSH_USER,
        'pass': settings.ANSIBLE_SSH_PASS
    }

    runner = Runner(hostnames=hostnames,
                    playbook=settings.ANSIBLE_PLAYBOOK,
                    private_key_file=settings.ANSIBLE_PUBLIC_KEY,
                    run_data=run_data,
                    become_pass=settings.ANSIBLE_SSH_PASS,
                    tags=tags)

    stats = runner.run()
