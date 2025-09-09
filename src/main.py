from argparse import ArgumentParser

SERVE='serve'
PREPROCESS='preprocess'

def mosaic():
    parser = ArgumentParser(description='Mosaic: A multi-tool for vehicular sensor data processing & visualization')
    
    # Common args
    parser.add_argument('--dir', type=str, help='Path to a ROS bag containing directory')
    
    subparsers = parser.add_subparsers(required=True, dest='command')

    # Serve command args
    serve_parser = subparsers.add_parser(SERVE, help='Serve an http xyz')
    serve_parser.add_argument('--foo', type=str, help='')

    # Preprocess command args
    preprocess_parser = subparsers.add_parser(PREPROCESS, help='Preprocess xyz')
    preprocess_parser.add_argument('--bar', type=str, help='')
    
    args = parser.parse_args()

    if args.command == SERVE:
        print(f'Serving')
    elif args.command == PREPROCESS:
        print(f'Preprocessing')
    else:
        parser.print_help()
        exit(1)

if __name__ == '__main__':
    mosaic()