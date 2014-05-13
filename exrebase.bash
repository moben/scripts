#!/bin/bash

EXPATH="${HOME}/Hacking/exherbo/repositories"

USE_TIG=1

# fail if without network
nm-online -x -q

is_online=$?

if [[ $# -ge 1 ]] ; then
	DIRS=()
	for repo in "$@" ; do
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
		git fetch --quiet 2> /dev/null
	fi

	remote_branch=$(git rev-parse --symbolic-full-name --abbrev-ref @{u} 2> /dev/null)

	[[ -z "${remote_branch}" ]] && continue

	# A...B is symmetric difference, which is the sum of commits on both branches since the last common ancestor
	if [[ $(git rev-list --count  ..."${remote_branch}") -gt 0 ]] ; then
		echo -e "\033[1;32m${PWD##*/}\033[0m"

		if [[ $(git rev-list --count  .."${remote_branch}") -gt 0 ]] ; then
			if [[ ${USE_TIG} == 1 ]] ; then
				tig -p -M10 -C -C --reverse .."${remote_branch}" ; true
			else
				git log --pretty=fuller -p -M10 -C -C --reverse .."${remote_branch}" ; true
			fi
		fi

		if [[ $(git rev-list --count  "${remote_branch}"..) -gt 0 ]] ; then
			git rebase -f "${remote_branch}" | grep --color -E -A100 '^Applying:' || true
		else
			git rebase -f -q "${remote_branch}" ; true
		fi
		[[ "${PIPESTATUS[0]}" -ne 0 ]] && git rebase --abort ; true
	fi

	nice git gc --quiet &

	popd "${dir}" &> /dev/null
done

