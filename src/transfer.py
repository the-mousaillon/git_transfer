import tarfile
from os import makedirs, unlink, environ
from os.path import join, exists
from shutil import rmtree, copytree
from git_transfer import COMMIT_EXPORT_PATH
from git.repo import Repo
from datetime import datetime

def get_repo_name(repo: Repo):
    repo_url = repo.remotes[0].config_reader.get("url")
    repo_name = repo_url.rstrip(".git").split("/")[-1]
    return repo_name


def extract_gitinore(source_repo_path: str):
    ignore_to_add = ""
    gitignore_path = join(source_repo_path, ".gitignore")
    write = False
    if not exists(gitignore_path):
        print("[INFO]: no gitinore found in source repo")
        return None

    print("[INFO]: gitinore found in source repo")
    with open(gitignore_path, "r") as gitignore_file:
        for line in gitignore_file:
            if "GIT_TRANSFER" in line:
                write = True
            
            if write:
                ignore_to_add += line
        
    return ignore_to_add

class RepoExporter:
    def __init__(self, source_repo_path, source_repo_branch, target_repo_path, target_repo_relative_directory, target_repo_commit_branch):
        self.source_repo_path = source_repo_path
        self.source_repo_branch = source_repo_branch
        self.target_repo_path = target_repo_path
        self.target_repo_commit_branch = target_repo_commit_branch
        
        # Instantiate repo objects
        self.source_repo = Repo(self.source_repo_path)
        self.target_repo = Repo(self.target_repo_path)

        # saving the head of the source repo
        self.source_head = self.source_repo.head.name

        # extract repo names
        self.source_repo_name = get_repo_name(self.source_repo)
        self.target_repo_name = get_repo_name(self.target_repo)

        # export paths
        self.target_repo_archive_path_root = "{}/{}".format(COMMIT_EXPORT_PATH, self.source_repo_name)
        self.target_repo_archive_path_tar = "{}/{}".format(self.target_repo_archive_path_root, "commit_archive.tar")
        self.target_repo_directory = "{}/{}".format(self.target_repo_path, target_repo_relative_directory)

        # ingores to add at each commit
        self.ignores_to_add = extract_gitinore(self.source_repo_path)
    
        # initialize commit infos
        self._exact_commits()

    def _clean_tmp(self):
        rmtree(COMMIT_EXPORT_PATH, ignore_errors=True)

    def _prepare_export(self):
        # clean the previous export data, recreate the forders
        rmtree(COMMIT_EXPORT_PATH, ignore_errors=True)
        rmtree(self.target_repo_directory, ignore_errors=True)

        makedirs(self.target_repo_archive_path_root, exist_ok=True)
        #makedirs(self.target_repo_directory, exist_ok=True)


    def _exact_commits(self):
        # going on the source branch
        self.source_repo.git.checkout(self.source_repo_branch)

        commits_infos = []
        for commit in self.source_repo.iter_commits():
            commit_id = commit.hexsha
            commit_infos = {
               # "author": commit.author,
                "message": commit.message,
                "date": datetime.fromtimestamp(commit.authored_date).isoformat()
            }
            print("found_commit --> ", commit_infos)
            
            commits_infos.append((commit_id, commit_infos))

        self.commits_infos = list(reversed(commits_infos))
        
        # Returning on the defaut HEAD
        self.source_repo.git.checkout(self.source_head)

    def _add_ignores(self):
        gitignore_path = join(self.source_repo_path, ".gitignore")
        if self.ignores_to_add is not None:
            with open(gitignore_path, "a") as gitignore_file:
                gitignore_file.write(self.ignores_to_add)

    def extract_source_files(self, commit_id: str):
        # clean the export tmp directory
        self._prepare_export()
        self.source_repo.git.checkout(commit_id, force=True)

        # get all the files of the commit
        with open(self.target_repo_archive_path_tar, "wb+") as export_archive_io:
            self.source_repo.archive(export_archive_io)
        
        # extract all the source files of the commit and remove the archive tar
        archive_tar = tarfile.open(self.target_repo_archive_path_tar)
        archive_tar.extractall(self.target_repo_archive_path_root)
        unlink(self.target_repo_archive_path_tar)
        
    def move_source_to_target(self):
        # copy the commit source files to the target repo
        copytree(self.target_repo_archive_path_root, self.target_repo_directory)
        
        # Add problematic files to gitignore

    def commit_to_target(self, commit_infos: dict):
        # tries to checkout to branch, creates the branch if it doesn't exists
        try:
            self.target_repo.git.checkout(b=self.target_repo_commit_branch)
        
        except Exception:
            self.target_repo.git.checkout(self.target_repo_commit_branch)

        self.target_repo.git.stage(".")
        self.target_repo.git.commit(**commit_infos)


    def transfer_commits(self):
        for commit_id, commit_infos in self.commits_infos:
            print("transfering commit --> ", commit_infos["message"])
            
            # faking commit date ;)
            environ["GIT_AUTHOR_DATE"] = commit_infos["date"]
            environ["GIT_COMMITTER_DATE"] = commit_infos["date"]

            self.extract_source_files(commit_id)
            self.move_source_to_target()
            self.commit_to_target(commit_infos)
    


    def __del__(self):
        self._clean_tmp()
