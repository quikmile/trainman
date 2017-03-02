from celery.task.base import task
from django.conf import settings

from ..base.ansibles import Runner
from ..servers.models import APIGateway
from ..services.models import ServiceNode


@task
def deploy_gateway():
    PLAYBOOK = settings.ANSIBLE_PLAYBOOK
    hosts = ['[gateway]']
    for gateway in APIGateway.objects.all():
        hosts.append('{} ansible_user={} ansible_sudo_pass={}'.format(gateway.server.ip_address,
                                                                      settings.ANSIBLE_SSH_USER,
                                                                      settings.ANSIBLE_SSH_PASS))

    run_data = {'services': ServiceNode.objects.all()}

    hostnames = '\n'.join(hosts)

    tags = ['prepare','nginx', 'gateway']

    runner = Runner(hostnames=hostnames,
                    playbook=PLAYBOOK,
                    private_key_file=settings.ANSIBLE_PUBLIC_KEY,
                    run_data=run_data,
                    become_pass=settings.ANSIBLE_SSH_PASS,
                    tags=tags)

    stats = runner.run()
