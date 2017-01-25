#!/bin/bash
echo "please make sure you have remote called ui-subtree pointing to github.com/DxCx/kodi-ui"
git remote update ui-subtree
git subtree pull --prefix=resources/lib/ui ui-subtree master
