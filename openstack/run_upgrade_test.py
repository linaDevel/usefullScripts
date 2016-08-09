from fuelweb_test import settings
from fuelweb_test.models.environment import EnvironmentModel
from fuelweb_test.settings import REPLACE_DEFAULT_REPOS_ONLY_ONCE, \
    REPLACE_DEFAULT_REPOS


def radosgw_started(remote):
    return remote.check_call('pkill -0 radosgw')['exit_code'] == 0

# Environment Settings

ENV_NAME = "Upgrade9X"

ENV_SETTINGS = {
    'volumes_lvm': False,
    'volumes_ceph': True,
    'images_ceph': True,
    'objects_ceph': True,
    'tenant': 'rados',
    'user': 'rados',
    'password': 'rados'
}

ENV_NODES = {
    'slave-01': ['controller'],
    'slave-02': ['controller'],
    'slave-03': ['controller'],
    'slave-04': ['compute', 'ceph-osd'],
    'slave-05': ['compute', 'ceph-osd'],
    'slave-06': ['compute', 'ceph-osd']
}

MIRROR_URL = "http://mirror.seed-cz1.fuel-infra.org/mos-repos/" \
             "ubuntu/snapshots/9.0-2016-08-08-094723/"

MIRRORS = ['mos9.0', 'mos9.0-holdback', 'mos9.0-hotfix',
           'mos9.0-proposed', 'mos9.0-security', 'mos9.0-updates']

# End of Environment Settings

ENV = EnvironmentModel(None)
FUEL_WEB = ENV.fuel_web

ENV.setup_environment()
ENV.make_snapshot("empty", is_make=True)

FUEL_WEB.get_nailgun_version()
FUEL_WEB.change_default_network_settings()

if REPLACE_DEFAULT_REPOS and REPLACE_DEFAULT_REPOS_ONLY_ONCE:
    FUEL_WEB.replace_default_repos()
ENV.make_snapshot("ready", is_make=True)

ENV.bootstrap_nodes(ENV.d_env.nodes().slaves[:6])

cluster_id = FUEL_WEB.create_cluster(
    name=ENV_NAME,
    mode=settings.DEPLOYMENT_MODE,
    settings=ENV_SETTINGS
)

FUEL_WEB.update_nodes(cluster_id, ENV_NODES)
FUEL_WEB.verify_network(cluster_id)

FUEL_WEB.deploy_cluster_wait(cluster_id)

FUEL_WEB.check_ceph_status(cluster_id)
FUEL_WEB.run_ostf(cluster_id=cluster_id, test_sets=['ha', 'smoke', 'sanity'])

with FUEL_WEB.get_ssh_for_node('slave-01') as remote:
    assert radosgw_started(remote), 'radosgw daemon started'

attrs = FUEL_WEB.client.get_cluster_attributes(cluster_id)
for mirror in MIRRORS:
    attrs['editable']['repo_setup']['repos']['value'].append({
        'name': mirror,
        'priority': 1050,
        'section': 'main restricted',
        'suite': mirror,
        'type': 'deb',
        'uri': MIRROR_URL,
    })
FUEL_WEB.client.update_cluster_attributes(cluster_id, attrs)

FUEL_WEB.redeploy_cluster_changes_wait_progress(cluster_id)

FUEL_WEB.verify_network(cluster_id)
FUEL_WEB.check_ceph_status(cluster_id)
FUEL_WEB.run_ostf(cluster_id=cluster_id, test_sets=['ha', 'smoke', 'sanity'])

with FUEL_WEB.get_ssh_for_node('slave-01') as remote:
    assert radosgw_started(remote), 'radosgw daemon started'

ENV.make_snapshot("upgrade_9x")
