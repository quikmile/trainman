from celery.task.base import task
from django.conf import settings

from ..base.ansibles import Runner
from ..servers.models import APIGateway
from ..services.models import ServiceNode


@task
def deploy_gateway():
    PLAYBOOK = settings.ANSIBLE_DIR + 'playbook.yml'
    hosts = ['[gateway]']
    for gateway in APIGateway.objects.all():
        hosts.append('{} ansible_user={} ansible_sudo_pass={}'.format(gateway.server.ip_address,
                                                                      settings.ANSIBLE_SSH_USER,
                                                                      settings.ANSIBLE_SSH_PASS))

    services = [{s.service.service_name,
                 s.service_version,
                 s.http_host,
                 s.http_port} for s in ServiceNode.objects.all()]

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
