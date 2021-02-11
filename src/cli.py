import argparse
from .transfer import RepoExporter

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-s", "--source", help="The source repository from which we want to transfer the commits", required=True)
    parser.add_argument("-sb", "--source-branch", help="The source branch from which we want to transfer the commits", required=True)
    parser.add_argument("-t", "--target", help="The target repository whom we want to transfer the commits to", required=True)
    parser.add_argument("-tb", "--target-branch", help="The target branch whom we want to transfer the commits to", required=True)
    parser.add_argument("-td", "--target-directory", help="The repository into which we want the source files to be copied", required=True)

    args = parser.parse_args()

    exporter = RepoExporter(args.source, args.source_branch, args.target, args.target_directory, args.target_branch)

    # start the exporting process
    exporter.transfer_commits()

if __name__ == "__main__":
    main()