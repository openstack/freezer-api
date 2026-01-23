#!/bin/bash -xe

# basic reference point for things like filecache
#
# TODO(sdague): once we have a few of these I imagine the download
# step can probably be factored out to something nicer

# Package source and version, all pkg files are expected to have
# something like this, as well as a way to override them.
ELASTICSEARCH_VERSION=${ELASTICSEARCH_VERSION:-9.2.4-amd64}
ELASTICSEARCH_BASEURL=${ELASTICSEARCH_BASEURL:-https://artifacts.elastic.co/downloads/elasticsearch}

# Elastic search actual implementation
function wget_elasticsearch {
    local file=${1}

    if [ ! -f ${FREEZER_API_FILES}/${file} ]; then
        wget $ELASTICSEARCH_BASEURL/${file} -O ${FREEZER_API_FILES}/${file}
    fi

    if [ ! -f ${FREEZER_API_FILES}/${file}.sha512 ]; then
        wget $ELASTICSEARCH_BASEURL/${file}.sha512 -O ${FREEZER_API_FILES}/${file}.sha512
    fi

    pushd ${FREEZER_API_FILES};  sha512sum ${file} > ${file}.sha512.gen;  popd

    if ! diff ${FREEZER_API_FILES}/${file}.sha512.gen ${FREEZER_API_FILES}/${file}.sha512; then
        echo "Invalid elasticsearch download. Could not install."
        return 1
    fi
    return 0
}

function download_elasticsearch {
    if is_ubuntu; then
        wget_elasticsearch elasticsearch-${ELASTICSEARCH_VERSION}.deb
    elif is_fedora || is_suse; then
        wget_elasticsearch elasticsearch-${ELASTICSEARCH_VERSION}.noarch.rpm
    fi
}

function configure_elasticsearch {
    # currently a no op
    :
}

function _check_elasticsearch_ready {
    # poll elasticsearch to see if it's started
    if ! wait_for_service 120 http://localhost:9200; then
        die $LINENO "Maximum timeout reached. Could not connect to ElasticSearch"
    fi
}

function start_elasticsearch {
    sudo /bin/systemctl start elasticsearch.service
    _check_elasticsearch_ready
}

function stop_elasticsearch {
    sudo /bin/systemctl stop elasticsearch.service
}

function install_elasticsearch {
    pip_install_gr elasticsearch
    if is_package_installed elasticsearch; then
        echo "Note: elasticsearch was already installed."
        return
    fi
    if is_ubuntu; then
        is_package_installed default-jre-headless || install_package default-jre-headless
        sudo dpkg -i ${FREEZER_API_FILES}/elasticsearch-${ELASTICSEARCH_VERSION}.deb
    elif is_fedora; then
        is_package_installed java-1.8.0-openjdk-headless || install_package java-1.8.0-openjdk-headless
        yum_install ${FREEZER_API_FILES}/elasticsearch-${ELASTICSEARCH_VERSION}.noarch.rpm
    elif is_suse; then
        is_package_installed java-1_8_0-openjdk-headless || install_package java-1_8_0-openjdk-headless
        zypper_install --no-gpg-checks ${FREEZER_API_FILES}/elasticsearch-${ELASTICSEARCH_VERSION}.noarch.rpm
    else
        echo "Unsupported install of elasticsearch on this architecture."
    fi
    sudo /bin/systemctl daemon-reload
    sudo /bin/systemctl enable elasticsearch.service
    usermod -a -G elasticsearch $USER
    /usr/share/elasticsearch/bin/elasticsearch-users useradd freezer -p ${DATABASE_PASSWORD} -r superuser
}

function uninstall_elasticsearch {
    if is_package_installed elasticsearch; then
        if is_ubuntu; then
            sudo apt-get purge elasticsearch
        elif is_fedora; then
            sudo dnf remove elasticsearch
        elif is_suse; then
            sudo zypper rm elasticsearch
        else
            echo "Unsupported install of elasticsearch on this architecture."
        fi
    fi
}

# The PHASE dispatcher. All pkg files are expected to basically cargo
# cult the case statement.
PHASE=$1
echo "Phase is $PHASE"

case $PHASE in
    download)
        download_elasticsearch
        ;;
    install)
        install_elasticsearch
        ;;
    configure)
        configure_elasticsearch
        ;;
    start)
        start_elasticsearch
        ;;
    stop)
        stop_elasticsearch
        ;;
    uninstall)
        uninstall_elasticsearch
        ;;
esac
