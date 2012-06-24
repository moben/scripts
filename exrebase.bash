#!/bin/bash

EXPATH="${HOME}/Hacking/exherbo"

# fail if without network
nm-online -x -q

is_online=$?

if [[ $# -ge 1 ]] ; then
	DIRS=()
	for repo in $@ ; do
		DIRS+=( "${EXPATH}/${repo}" )
	done
else
	DIRS=( "${EXPATH}"/* )
fi

# fail if any command fails
#set -e
# fail if any variable is undefined
set -u

#IFS='\0' find "${EXPATH}" -maxdepth 3 -type d -print0 | while read -d $'\0' dir ; do
for dir in "${DIRS[@]}" ; do
	! [[ -d "${dir}"/.git ]] && continue

	pushd "${dir}" &> /dev/null

	if [[ $is_online -eq 0 ]] ; then
		git fetch --quiet
	fi
	if ! git diff --quiet master..origin/master ; then
		echo -e "\033[1;32m$(basename "${PWD}")\033[0m"
		git log --pretty=fuller -p -M10 -C -C --reverse master..origin/master ; true
		git rebase -f origin/master | grep --color -E -A100 '^Applying:' || true
		[[ "${PIPESTATUS[0]}" -ne 0 ]] && git rebase --abort ; true
	fi

	nice git gc --quiet &

	popd "${dir}" &> /dev/null
done

