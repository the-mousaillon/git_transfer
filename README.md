# Git Transfer

This package make it possible to transfer a git repository into another, without losing the commit history !!

## How to

Execute the cli for the package parent directory:

```
 python -m git_transfer.src.cli [-h] -s SOURCE -sb SOURCE_BRANCH -t TARGET -tb TARGET_BRANCH -td TARGET_DIRECTORY
 ```

Then, the source repo commit history will be copied into the specified folder in the target repository. You also have to specify the target repository's branch to whom the commit history will be transfered.

