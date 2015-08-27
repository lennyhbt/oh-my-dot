#!/usr/bin/env python3

import sys, os
from datetime import datetime
from optparse import OptionParser
from pylibs.linkdot import remove_bad_symlink, make_symlink_stack, do_actions, LINKREC


HOME_PATH = os.environ['HOME']
BASE_PATH = os.path.dirname(os.path.realpath(sys.argv[0]))

def make_all_links(target_path, fake_operate):
    linkrec = os.path.join(BASE_PATH, LINKREC)
    remove_bad_symlink(linkrec)

    linkdirs = os.path.join(BASE_PATH, 'linkdirs')
    linkfiles = os.path.join(BASE_PATH, 'linkfiles')

    actions = make_symlink_stack(linkdirs, target_path)
    actions += make_symlink_stack(linkfiles, target_path, top_level=False)
    do_actions(actions, fake_operate)


def do_post_install(target_path):
    # chsh to zsh
    os.system("chsh -s /bin/zsh")

    # vim post installs
    os.system("mkdir {0}/.vim/.backup".format(target_path))
    os.system("mkdir {0}/.vim/.swap".format(target_path))
    os.system("mkdir {0}/.vim/.undofiles".format(target_path))
    os.system("git clone https://github.com/gmarik/vundle.git {0}/.vim/bundle/vundle".format(target_path))

    link_target= "{target_path}/.vimrc".format(target_path=target_path)
    linkname = "{target_path}/.vim/vimrc".format(target_path=target_path)
    if os.path.lexists(link_target) and os.path.realpath(link_target) != linkname:
        postfix = str(datetime.timestamp(datetime.now()))
        os.system('mv {0} {1}'.format(link_target, link_target + '.' + postfix))
    os.system("ln -s {target_path}/.vim/vimrc {target_path}/.vimrc".format(target_path=target_path))
    os.system("vim +PluginInstall +qall")
    print('plugin install')
    #os.system("~/.vim/bundle/YouCompleteMe/install.py --clang-completer --omnisharp-completer --gocode-completer")
    os.system("~/.vim/bundle/YouCompleteMe/install.py --clang-completer")


if __name__ == '__main__':
    # parse options
    parser = OptionParser()
    parser.add_option("-f", "--fake", dest="fake",
            action="store_true", default=False, help="only print the actions")
    parser.add_option("-p", "--post", dest="post",
            action="store_true", default=False, help="only do post install")
    parser.add_option("-t", "--target", dest="target",
            default=HOME_PATH, help="install target dir")
    (options, args) = parser.parse_args()

    fake_option = False
    if options.fake:
        fake_option = True
    target_path = options.target

    if options.post:
        do_post_install(target_path)
    else:
        os.chdir(BASE_PATH)
        os.system("git submodule init")
        os.system("git submodule update")
        # do real options
        make_all_links(target_path, fake_option)
        if not fake_option:
            do_post_install(target_path)
