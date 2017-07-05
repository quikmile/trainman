import json

from celery.task.base import task
from django.conf import settings

from .models import ServiceRegistryNode, ServiceNode, TrellioAdmin
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
def deploy_service(service_node_id, **options):
    service_node = ServiceNode.objects.get(pk=service_node_id)

    if options.get('database'):
        database = service_node.get_database()
        database.deploy()

    PLAYBOOK = settings.ANSIBLE_PLAYBOOK
    hosts = ['[trellio_service]']

    host = service_node.instance.server.ip_address

    hosts.append('{} ansible_user={} ansible_sudo_pass={}'.format(host,
                                                                  settings.ANSIBLE_SSH_USER,
                                                                  settings.ANSIBLE_SSH_PASS))

    tags = ['service']
    if options.get('tags'):
        tags.extend(options.get('tags'))

    gitlab_config = service_node.get_config_file()
    gitlab_config_dict = json.loads(gitlab_config['config_content'])

    config = service_node.get_config()
    config['SERVICE_NAME'] = gitlab_config_dict['SERVICE_NAME']

    run_data = {
        'project_root': gitlab_config['config_path'].split('/')[0],
        'config_path': gitlab_config['config_path'],
        'pip_repo_url': service_node.pip_repo_url,
        'git_repo_url': service_node.git_repo_url,
        'project_name': service_node.service_verbose_name,
        'service_name': config['SERVICE_NAME'],
        'gitlab_username': settings.GITLAB_USERNAME,
        'gitlab_password': settings.GITLAB_PASSWORD,
        'service_config': json.dumps(config, sort_keys=True, indent=2, separators=(',', ': '))
    }

    hostnames = '\n'.join(hosts)

    runner = Runner(hostnames=hostnames,
                    playbook=PLAYBOOK,
                    private_key_file=settings.ANSIBLE_PUBLIC_KEY,
                    run_data=run_data,
                    become_pass=settings.ANSIBLE_SSH_PASS,
                    tags=tags)

    stats = runner.run()

    if options.get('tags') and 'prepare' in options.get('tags'):
        deploy_gateway.delay()


@task
def deploy_trellio_admin(trellio_admin_id, extra_tags=()):
    trellio_admin = TrellioAdmin.objects.get(pk=trellio_admin_id)

    PLAYBOOK = settings.ANSIBLE_PLAYBOOK
    hosts = ['[trellio_admin]']

    host = trellio_admin.server.ip_address

    hosts.append('{} ansible_user={} ansible_sudo_pass={}'.format(host,
                                                                  settings.ANSIBLE_SSH_USER,
                                                                  settings.ANSIBLE_SSH_PASS))
    tags = list(extra_tags) + ['trellioadmin']
    if 'setup' in tags:
        tags.append('nginx')

    services = []
    for service in trellio_admin.service_set.all():
        database = service.get_database()

        data = dict()
        data['service'] = service.service_uri
        data['database'] = database.get_database_settings()

        services.append(data)

    run_data = {
        'hostname': trellio_admin.domain,
        'email': trellio_admin.project_owner,
        'project_root': '/srv',
        'project_name': 'trellioadmin',
        'project_src': 'trellioadmin',
        'environment_variables': trellio_admin.get_environment_variables(),
        'db_name': trellio_admin.get_db_name(),
        'db_user': trellio_admin.get_db_user(),
        'db_pass': trellio_admin.get_db_pass(),
        'services': services
    }

    hostnames = '\n'.join(hosts)

    runner = Runner(hostnames=hostnames,
                    playbook=PLAYBOOK,
                    private_key_file=settings.ANSIBLE_PUBLIC_KEY,
                    run_data=run_data,
                    become_pass=settings.ANSIBLE_SSH_PASS,
                    tags=tags)

    stats = runner.run()
