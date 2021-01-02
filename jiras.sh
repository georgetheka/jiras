#!/usr/bin/env bash

CONNECTION_STRING=postgres://jiras:jiras@localhost:5432/jiras
URL_REGEX='(https?|ftp|file)://[-A-Za-z0-9\+&@#/%?=~_|!:,.;]*[-A-Za-z0-9\+&@#/%=~_|]'
INT_REGEX='^[1-9][0-9]+$'
DEFAULT_QUERY_LIMIT="1000"

usage() {
    cat << EOF
Usage: jiras -- runs the jira etl process

SYNOPSIS
    jiras [-h | -j <jira-server-url> -q <jira-query> [-l <jira-query-limit>]]

OPTIONS
    -h      : displays usage information
    -j      : specify the jira server url (e.g. https://myjirainstance.example.com)
    -q      : specify the jira query statement (e.g. "project in (X, Y, Z)")
    -l      : specify the jira query limit (e.g. 150), defaults to "${DEFAULT_QUERY_LIMIT}"

EOF
}

usage_and_exit() {
    local message="$1"
    >&2 echo "ERROR: $message"
    >&2 echo "-----------------------------------------"
    usage 1>&2
    exit -1
}

main() {
    local jira_query_limit="$DEFAULT_QUERY_LIMIT"
    local jira_server=
    local jira_query=

    while getopts "hj:q:l:" o; do
      case ${o} in
        h)
            usage && exit 0
          ;;
        j)
            if [[ $OPTARG =~ $URL_REGEX ]]; then
                jira_server="$OPTARG"
            else
                usage_and_exit "Invalid jira server url for option -j"
            fi
          ;;
        q)
            jira_query="$OPTARG"
          ;;
        l)
            if [[ $OPTARG =~ $INT_REGEX ]]; then
                jira_query_limit="$OPTARG"
            else
                usage_and_exit "Invalid jira query limit value for option -l"
            fi
          ;;
        \?)
            usage_and_exit "Invalid option -$OPTARG"
          ;;
      esac
    done
    shift $((OPTIND -1))

    if [[ -z ${jira_server} ]]; then
        usage_and_exit "Missing required argument: -j (jira server url)"
    fi
    if [[ -z ${jira_query} ]]; then
        usage_and_exit "Missing required argument: -q (jira query statement)"
    fi

    python jiras.py "$jira_server" "$jira_query" ${jira_query_limit}
}

main "$@"
