# check for service enabled
if is_service_enabled freezer-api; then
    if [[ "$1" == "source" || "`type -t install_freezer_api`" != 'function' ]]; then
        # Initial source
        source $FREEZER_API_DIR/devstack/lib/freezer-api
    fi

    if [[ "$1" == "stack" && "$2" == "install" ]]; then
        echo_summary "Installing Freezer API"
        install_freezer_api
    elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
        echo_summary "Configuring Freezer API"
        configure_freezer_api
        echo_summary "Creating keystone accounts for Freezer API"
        create_freezer_api_accounts
    elif [[ "$1" == "stack" && "$2" == "extra" ]]; then
        echo_summary "Initializing Freezer API"
        init_freezer_api
        start_freezer_api
    fi

    if [[ "$1" == "unstack" ]]; then
        stop_freezer_api
    fi

    if [[ "$1" == "clean" ]]; then
        cleanup_freezer_api
    fi
fi