import argparse
import datetime

from . import System


def main():
    argument_parser = argparse.ArgumentParser(
        prog = "scrapper",
        description = ""
    )

    sub_parsers = argument_parser.add_subparsers()

    argument_parser.add_argument(
        "-d", "--debug",
        help = "Turns on debug mode.",
        action = "store_true"
    )



    create_subparser = sub_parsers.add_parser(
        "create",
        help=System().phrase_table["CREATE_HELP"]
        )
    create_subparser.add_argument(
        "name",
        help=System().phrase_table["CREATE_NAME_HELP"]
        )



    remove_subparser = sub_parsers.add_parser(
        "remove",
        help=System().phrase_table["REMOVE_HELP"]
        )
    remove_subparser.add_argument(
        "names",
        help=System().phrase_table["REMOVE_NAMES_HELP"],
        nargs="+"
        )
    remove_subparser.add_argument(
        "-f",
        "--force",
        help=System().phrase_table["REMOVE_FORCE_HELP"],
        action="store_true"
        )



    rename_subparser = sub_parsers.add_parser(
        "rename",
        help=System().phrase_table["RENAME_HELP"]
        )
    rename_subparser.add_argument(
        "old_name",
        help=System().phrase_table["RENAME_OLD_NAME_HELP"]
        )
    rename_subparser.add_argument(
        "new_name",
        help=System().phrase_table["RENAME_NEW_NAME_HELP"]
        )
    rename_subparser.add_argument(
        "-f",
        "--force",
        help=System().phrase_table["RENAME_FORCE_HELP"],
        action="store_true"
        )



    run_subparser = sub_parsers.add_parser(
        "run",
        help=System().phrase_table["RUN_HELP"]
        )
    run_subparser.add_argument(
        "name",
        help=System().phrase_table["RUN_NAME_HELP"]
        )
    run_subparser.add_argument(
        "-a",
        "--arguments",
        help=System().phrase_table["RUN_ARGUMENTS_HELP"],
        nargs="+"
        )
    run_subparser.add_argument(
        "-d",
        "--dev",
        help=System().phrase_table["RUN_DEV_HELP"],
        action="store_true"
        )



    clean_logs_subparser = sub_parsers.add_parser(
        "clean_logs",
        help=System().phrase_table["CLEAN_LOGS_HELP"]
        )
    clean_logs_subparser.add_argument(
        "-s",
        "--scrappers",
        help=System().phrase_table["CLEAN_LOGS_SCRAPPERS_HELP"],
        default="main")
    clean_logs_subparser.add_argument(
        "-e",
        "--excepted",
        help=System().phrase_table["CLEAN_LOGS_EXCEPTED_HELP"]
        )



    export_subparser = sub_parsers.add_parser(
        "export",
        help=System().phrase_table["EXPORT_HELP"]
        )
    export_subparser.add_argument(
        "name",
        help=System().phrase_table["EXPORT_NAME_HELP"]
        )
    export_subparser.add_argument(
        "path",
        help=System().phrase_table["EXPORT_PATH_HELP"]
        )



    import_subparser = sub_parsers.add_parser(
        "import",
        help=System().phrase_table["IMPORT_HELP"]
        )
    import_subparser.add_argument(
        "path",
        help=System().phrase_table["IMPORT_PATH_HELP"]
        )



    schadule_subparser = sub_parsers.add_parser(
        "shadule",
        help=System().phrase_table["SCHADULE_HELP"]
        )
    schadule_subparser.add_argument(
        "name",
        help=System().phrase_table["SCHADULE_NAME_HELP"]
        )
    schadule_subparser.add_argument(
        "frequency",
        choices=("once", "hourly", "daily", "monthly", "onstart"),
        help=System().phrase_table["SCHADULE_FREQUENSY_HELP"]
        )
    schadule_subparser.add_argument(
        "-t",
        "--time",
        type=datetime.time,
        help=System().phrase_table["SCHADULE_TIME_HELP"]
        )
    schadule_subparser.add_argument(
        "-r",
        "--release",
        help=System().phrase_table["SCHADULE_RELEASE_HELP"]
        )



    test_subparser = sub_parsers.add_parser(
        "test",
        help=System().phrase_table["TEST_HELP"]
        )
    test_subparser.add_argument(
        "name",
        help=System().phrase_table["TEST_NAME_HELP"]
        )



    release_subparser = sub_parsers.add_parser(
        "release",
        help=System().phrase_table["RELEASE_HELP"]
        )
    release_subparser.add_argument(
        "name",
        help=System().phrase_table["RELEASE_NAME_HELP"]
        )
    release_subparser.add_argument(
        "release",
        help=System().phrase_table["RELEASE_RELEASE_HELP"]
        )


    arguments = argument_parser.parse_args()
    if arguments.debug:
        System().set_debug()


if __name__ == "__main__":
    main()
