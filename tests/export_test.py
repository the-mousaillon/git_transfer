from git_transfer.src.transfer import RepoExporter

SOURCE_REPO = "/home/bzh/Documents/Happn/SCAM/batch_brother"
SOURCE_REPO_BRANCH = "master"
TARGET_REPO = "/home/bzh/Documents/Happn/angularJS_libs"

TARGET_REPO_DIR = "batch_brother_export_test"
TARGET_REPO_BRANCH = "puffy"

if __name__ == "__main__":
    exporter = RepoExporter(SOURCE_REPO, SOURCE_REPO_BRANCH, TARGET_REPO, TARGET_REPO_DIR, TARGET_REPO_BRANCH)
    
    exporter.target_repo.git.checkout("master")
    
    # deleting the branch
    try:
        exporter.target_repo.git.branch(D=TARGET_REPO_BRANCH)
    except Exception:
        pass
    
    exporter.transfer_commits()