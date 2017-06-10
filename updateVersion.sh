#!/bin/bash

git checkout master
git remote update origin
git reset --hard origin/master

NEW_VERSION=`python updateVersion.py`
BRANCH_NAME=version-${NEW_VERSION}

git checkout -b ${BRANCH_NAME}
git add addon.xml
echo -e "[B]${NEW_VERSION}[/B]\n- " > changelog_update
vim changelog_update
cat changelog.txt >> changelog_update
mv changelog_update changelog.txt
git add changelog.txt
git commit -m "chore(addon): update to version ${NEW_VERSION}"
git tag v${NEW_VERSION}
git push -u --tags origin ${BRANCH_NAME}
git checkout master
echo "Done: https://github.com/DxCx/plugin.video.9anime/compare/${BRANCH_NAME}?expand=1"
