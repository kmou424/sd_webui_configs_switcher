import argparse
import os
import subprocess
import os.path as path

CONFIGS_ROOT = "custom_configs"
CONFIGS_FILES = [
    "config.json", "ui-config.json"
]


def parse_arg():
    arg_parser = argparse.ArgumentParser(description="Configuration switcher for stable-diffusion-webui")
    mutually_exclusive_main_group = arg_parser.add_mutually_exclusive_group()
    mutually_exclusive_main_group.add_argument(
        '-l', '--list',
        action='store_true',
        help="show available configurations"
    )
    mutually_exclusive_main_group.add_argument(
        '-s', '--switch',
        default=None,
        type=str,
        metavar='[CONFIG_NAME]',
        help="search configuration by name and switch to it"
    )
    return arg_parser.parse_args()


def run_cmd(cmd: str):
    print("Execute command: %s" % cmd)
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)


def root_check():
    assert os.getuid() == 0 and os.getgid() == 0, "you must run this script with root permission"


def env_check():
    assert path.exists(CONFIGS_ROOT), "\"configs\" directory not found, we can't locate your configurations for " \
                                      "switch"


def check_action(args):
    if args.list:
        print("> Below are available configurations: ")
        for _ in sorted(filter(lambda d:
                               path.isdir(path.join(CONFIGS_ROOT, d))
                               and path.exists(path.join(CONFIGS_ROOT, d))
                               and check_config_files_exist(d, assert_check=False),
                               os.listdir(CONFIGS_ROOT))): print(_)
        return
    if args.switch:
        root_check()
        check_config_files_exist(args.switch)
        clean_and_create_link(args.switch)


def check_config_files_exist(config_name, assert_check=True):
    target_config_directory = path.join(CONFIGS_ROOT, config_name)
    if assert_check:
        assert path.isdir(target_config_directory) and path.exists(target_config_directory), \
            "target config directory is not exist: %s" % target_config_directory
    else:
        if not path.isdir(target_config_directory) and path.exists(target_config_directory):
            return False
    for config_file in CONFIGS_FILES:
        if assert_check:
            assert path.isfile(path.join(target_config_directory, config_file)) and \
                   path.exists(path.join(target_config_directory, config_file)), \
                   "required config file \"%s\" is not in \"%s\"" % (config_file, target_config_directory)
        else:
            if not path.isfile(path.join(target_config_directory, config_file)) and \
                    path.exists(path.join(target_config_directory, config_file)):
                return False
    if not assert_check:
        return True


def clean_and_create_link(config_name):
    target_config_directory = path.join(CONFIGS_ROOT, config_name)
    for config_file in CONFIGS_FILES:
        if path.exists(config_file):
            if path.islink(config_file):
                os.remove(config_file)
            else:
                print("failed create link for \"%s\": target is not a symbolic link" % config_file)
                continue
        run_cmd("ln -sT %s %s" % (path.join(target_config_directory, config_file), config_file))


def main():
    env_check()
    check_action(parse_arg())


if __name__ == '__main__':
    main()
