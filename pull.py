import os
import sys
import json
import argparse
import urllib.request

# parameter
parser = argparse.ArgumentParser(description = 'Clone from the https://anonymous.4open.science')
parser.add_argument('--dir', type = str, default = 'master', help = 'master location')
parser.add_argument('--target', type = str, help = 'anonymous link you want to clone')
parser.add_argument('--force', action='store_true', help = 'force to cover the existing files')

# headers = {'User-Agent': user_agent}
user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; X64)'
opener = urllib.request.build_opener()
opener.addheaders = [('User-Agent', user_agent)]
urllib.request.install_opener(opener)


# normal url to api
def to_api(url: str) -> str:
    return url.replace('/r/', '/api/repo/')


def urljoin(url: str, append: str) -> str:
    return url.rstrip('/') + '/' + append


# parse dir tree
# { 'file': {'size': num}, 'dir': {'file': {'size': num}} }
def parse_dir_tree(tree: dict) -> list:
    file_tree = []
    for key in tree.keys():
        if 'size' in tree[key].keys():
            file_tree.append(key)
        else:
            file_tree.append({key: parse_dir_tree(tree[key])})
        # if 'size'
    # for key
    return file_tree


# obtain dir tree from url
def obtain_file_list(url: str) -> list:
    with urllib.request.urlopen(urljoin(url, 'files')) as response:
        resp = response.read()
    contents = json.loads(str(resp, encoding = 'utf-8'))
    return parse_dir_tree(contents)


def download(file_list: list, url: str, dir_name: str, is_force: bool = False) -> None:
    for item in file_list:
        if isinstance(item, str):
            file = os.path.join(dir_name, item)
            if os.path.exists(file) and not is_force:
                sys.stdout.write('%s has found, skip!\n' % file)
            else:
                sys.stdout.write('download %s ...\n' % file)
                urllib.request.urlretrieve(urljoin(url, item), file)
        elif isinstance(item, dict):
            subdir = list(item.keys())[0]
            subdir_path = os.path.join(dir_name, subdir)
            if not os.path.exists(subdir_path):
                os.mkdir(subdir_path)
            download(item[subdir], urljoin(url, subdir), subdir_path, is_force)
        else:
            sys.stderr.write('Type [%s] error!\n' % str(type(item)))
            sys.exit(-1)
        # end if
    # end for


def main(dir_name: str, target: str, is_force: bool = False) -> None:
    # make dir
    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)
    elif os.path.isfile(dir_name):
        sys.stderr.write('%s is a file, break!\n' % dir_name)
        sys.exit(-1)

    # obtain file list
    url = to_api(target)
    file_list = obtain_file_list(url)

    # download
    download(file_list, urljoin(url, 'file'), dir_name, is_force)


if __name__ == '__main__':
    args = parser.parse_args()
    assert args.target, '\nPlease specifipy your target URL, \n e.g:\tpython pull.py' \
                        '--target https://anonymous.4open.science/r/99219ca9-ff6a-49e5-a525-c954080de8a7'

    main(args.dir, args.target, args.force)
