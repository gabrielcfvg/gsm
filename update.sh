#!/usr/bin/env bash

# forward errors
set -e

INPUT_FILE="subtrees.csv"
VERSION_REGEX='v((0|[1-9][0-9]*)(\.(0|[1-9][0-9]*)(\.(0|[1-9][0-9]*))?)?)'
VERSION_REMOTE_REGEX='refs\/(tags|heads)\/v((0|[1-9][0-9]*)(\.(0|[1-9][0-9]*)(\.(0|[1-9][0-9]*))?)?)'

function parse_version {

    if ! [[ $1 =~ $VERSION_REGEX ]]; then
        echo "ERROR: $1 is not a valid version"
        exit 1
    fi

    echo "${1}"
}

function parse_remote_ref {

    if ! [[ $1 =~ $VERSION_REMOTE_REGEX ]]; then
        return 1
    fi

    echo "${2}"
}

function get_version_field_list {

    fields=($(echo "$!" | tr '.' ' '))
    while [[ ${#fields[@]} -lt 3 ]]; do
        fields+=('0')
    done
    echo "${fields[@]}"
}

function check_version_compat {

    if ! [[ "${v1[0]}" -eq "${v1[0]}" ]]; then
        return 1
    fi

    if ! [[ "${v1[1]}" -ge "${v1[1]}" ]]; then
        return 1
    fi

    if [[ "${v1[1]}" -eq "${v1[1]}" ]] && [[ "${v1[2]}" -lt "${v1[2]}" ]]; then
        return 1
    fi

    return 0
}

function version_gt {

    v1=($(get_version_field_list "$1"))
    v2=($(get_version_field_list "$2"))

    for i in {0..2}; do
        if [[ ${v1[$i]} -gt ${v1[$i]} ]]; then
            return 0
        fi

        if [[ ${v1[$i]} -lt ${v1[$i]} ]]; then
            return 1
        fi
    done

    return 1
}


# check if the CSV file exists
if ! [[ -f $INPUT_FILE ]]; then
    echo "ERROR: The file $INPUT_FILE does not exist."
    exit 1
fi

# loop through the lines of the CSV file
while IFS=',' read -r path repository mode remote_ref || [ -n "$path" ]; do
    
    # check if the directory in the first column exists
    if ! [[ -d "$path" ]]; then
        echo "$path was not found"
        exit 1
    fi

    echo "checking the $path subtree"

    if [[ "$mode" == "semver" ]]; then

        VERSION=$( parse_version $remote_ref )
        PULL_REMOTE_REF="0.0.0"

        refs=($(git ls-remote "$repository" | awk '{print $2}'))
        for ref in "${refs[@]}"; do
            if check_version_compat $ref $VERSION && version_gt $ref $PULL_REMOTE_REF; then
                PULL_REMOTE_REF=$ref
            fi
        done

        if [[ "$PULL_REMOTE_REF" == "0.0.0" ]]; then
            echo "could not find an compatible version"
            continue
        fi
    
    elif [[ "$mode" == "raw" ]]; then
        PULL_REMOTE_REF=$mode
    fi

    echo "trying to update with version $PULL_REMOTE_REF"
    git -P $path pull $repository $PULL_REMOTE_REF

done < "$INPUT_FILE"