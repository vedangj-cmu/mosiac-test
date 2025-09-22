from argparse import ArgumentParser

from ingest import ingest

SERVE = "serve"
INGEST = "ingest"


def mosaic():
    parser = ArgumentParser(
        description="Mosaic: A multi-tool for vehicular sensor data processing & visualization"
    )

    subparsers = parser.add_subparsers(required=True, dest="command")

    # Serve command args
    serve_parser = subparsers.add_parser(SERVE, help="Serve an http xyz")
    serve_parser.add_argument("--foo", type=str, help="")

    # Ingest command args
    ingest_parser = subparsers.add_parser(INGEST, help="Ingest rosbags")
    ingest_parser.add_argument(
        "--src", type=str, help="Path to a ROS bag containing directory", required=True
    )
    ingest_parser.add_argument(
        "--dest", type=str, help="Where to put the new rosbags", required=True
    )

    args = parser.parse_args()

    if args.command == SERVE:
        raise NotImplementedError
    elif args.command == INGEST:
        print("Ingesting")
        ingest(bag_path=args.src, img_path=args.dest)
    else:
        parser.print_help()
        exit(1)


if __name__ == "__main__":
    mosaic()
